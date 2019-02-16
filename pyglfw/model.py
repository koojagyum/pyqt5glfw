import json
import numpy as np
import os
import pyrr
import random

from .camera import Camera
from .light import DirectionalLight
from .material import load_material
from .renderer import Renderer
from .renderer import resource_path

from OpenGL.GL import *
from pyglfw.framework import IndexObject
from pyglfw.framework import VertexObject


verbose = True


def debug(msg):
    if verbose:
        print(msg)


def load_model(desc, basepath='.'):
    def _pick(key, dic, default=None):
        if key not in dic:
            return default
        return dic[key]

    def _pick_nparray(key, dic, dtype=np.float32):
        if key not in dic:
            return None
        return np.asarray(dic[key], dtype=dtype)

    def _pick_path(key, dic, default=None):
        if key not in dic:
            return default
        return os.path.join(basepath, dic[key])

    vertices = _pick_nparray('vertices', desc, dtype=np.float32)
    edges = _pick_nparray('edges', desc, dtype=np.uint16)
    faces = _pick_nparray('faces', desc, dtype=np.uint16)
    color = _pick_nparray('color', desc, dtype=np.float32)
    material_desc = _pick('material', desc)

    attrs = None
    key_attr = 'attributes'
    if key_attr in desc:
        attrs = desc[key_attr]
        for key, value in attrs.items():
            attrs[key] = np.array(value, dtype=np.float32)

    name = None
    if 'name' in desc:
        name = desc['name']

    color_model = ColorModel(
        name=name,
        vertices=vertices,
        edges=edges,
        faces=faces,
        color=color,
        attributes=attrs.copy()
    )

    if material_desc is not None:
        attrs.pop('color', None)
        material = load_material(material_desc, basepath)
        material_model = TextureModel(
            name=name,
            vertices=vertices,
            edges=edges,
            faces=faces,
            attributes=attrs,
            material=material
        )
        return material_model

    return color_model


def load_fromjson(jsonpath):
    with open(jsonpath) as f:
        desc = json.load(f)
        basepath = os.path.dirname(jsonpath)
        return load_model(desc, basepath)

    return None


class ColorModel:

    ATTR_ORDER = [
        # 'position',
        'color',
        'normal',
    ]

    def __init__(self,
                 name='',
                 vertices=None,
                 edges=None, faces=None,
                 color=None, attributes=None,
                 draw_point=True,
                 wireframe=False):
        self.name = name
        self._vertices = None
        self._color = None
        self._attrs = {}
        self._vertices_pending = None
        self._color_pending = None
        self._attrs_pending = None
        self.draw_point = draw_point

        self._vertexobj = None
        self._indexobj_edges = None
        self._indexobj_faces = None

        self.draw_mode = 'points'

        self.vertices = vertices
        self.attrs = attributes
        self.wireframe = wireframe

        if color is None and \
           (attributes is None or \
            'color' not in attributes):
            color = (
                random.random(),
                random.random(),
                random.random()
            )
        self.color = color

        self._edges = edges
        self._faces = faces

    def prepare(self):
        self._check_ebo()

    def draw(self, program):
        self._update_geometry()

        if self._vertexobj is None:
            return

        with self._vertexobj as vo:
            if self.draw_point:
                glPointSize(8)
                glDrawArrays(GL_POINTS, 0, vo.vertex_count)
            if self._indexobj_edges is not None:
                with self._indexobj_edges as ebo:
                    glDrawElements(
                        GL_LINES,
                        ebo.count,
                        GL_UNSIGNED_SHORT,
                        None
                    )
            if self._indexobj_faces is not None:
                with self._indexobj_faces as ebo:
                    if self.wireframe:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                    glDrawElements(
                        GL_TRIANGLES,
                        ebo.count,
                        GL_UNSIGNED_SHORT,
                        None
                    )
                    if self.wireframe:
                        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def dispose(self):
        self._indexobj_edges = None
        self._indexobj_faces = None

    def _check_ebo(self):
        if self._edges is not None and \
           self._indexobj_edges is None:
            self._indexobj_edges = IndexObject(self._edges)
        if self._faces is not None and \
           self._indexobj_faces is None:
            self._indexobj_faces = IndexObject(self._faces)

    def _update_geometry(self):
        self._check_ebo()

        if not self._check_pending_data():
            return

        v = self._build_data()

        if self._vertexobj is not None and \
           self._vertexobj.update(v):
            return

        self._vertexobj = VertexObject(
            v,
            self._alignment
        )

    def _check_pending_data(self):
        pending_check = self._vertices_pending is None and \
                        self._color_pending is None and \
                        self._attrs_pending is None
        if pending_check:
            return False

        if self._vertices_pending is not None:
            self._vertices = self._vertices_pending
            self._vertices_pending = None

        # It does not make sense that color(or others) would be
        # updated without any vertices
        if self.vertices is None:
            return False

        if self._color_pending is not None:
            self._color = self._color_pending
            self._color_pending = None

        if self._attrs_pending is not None:
            self._attrs = self._attrs_pending
            self._attrs_pending = None

        return True

    def _build_data(self):

        def _concat_withname(v, name):
            if name in self.attrs:
                return np.column_stack((v, self.attrs[name]))
            return v

        if self.color is not None:
            self.attrs['color'] = self._get_colors(self.vertices.shape[0])

        v = self.vertices
        if self.attrs is not None:
            for attr_name in self.ATTR_ORDER:
                # if attr_name == 'position':
                #     continue
                v = _concat_withname(v, attr_name)

        return v

    def _get_colors(self, num):
        color = np.array((self.color), dtype='float32')
        colors = np.tile(color, num).reshape((num, 3))
        return colors

    def _concat_withcolors(self, v):
        num = v.shape[0]
        colors = self._get_colors(num)
        return np.column_stack((v, colors))

    def _concat_withattrs(self, v, attrs):
        data = v
        for attr in attrs:
            data = np.column_stack((data, attr))
        return data

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, value):
        self._vertices_pending = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color_pending = value
        if value is not None and \
           self._attrs_pending is not None and \
           'color' in self._attrs_pending:
            self._attrs_pending.pop('color', None)

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, value):
        self._attrs_pending = value
        if value is not None and \
           self._attrs_pending is not None and \
           'color' in self._attrs_pending:
            self._color_pending = None

    @property
    def _alignment(self):
        a = [self.vertices.shape[1]]

        for attr_name in self.ATTR_ORDER:
            if attr_name in self.attrs:
                a.append(self.attrs[attr_name].shape[1])

        return a

    @property
    def use_material(self):
        return False


class ModelRenderer(Renderer):

    default_vs_path = resource_path('./shader/model_color_light.vs')
    default_fs_path = resource_path('./shader/model_color_light.fs')

    def __init__(self, name='', model=None, camera=None, lights=[]):
        super().__init__(
            vs_path=self.default_vs_path,
            fs_path=self.default_fs_path,
            name=name
        )
        self.model = model
        self.camera = camera
        self.lights = lights

    def prepare(self):
        super().prepare()
        with self._program as p:
            if self.camera is None:
                p.setMatrix4(
                    'projection',
                    pyrr.matrix44.create_identity()
                )
            else:
                p.setMatrix4('projection', self.camera.proj_matrix)
            p.setMatrix4('model', pyrr.matrix44.create_identity())

        if self.model is not None:
            self.model.prepare()

    def render(self):
        if self.model is None:
            return

        with self._program as p:
            if self.camera is None:
                p.setMatrix4('view', pyrr.matrix44.create_identity())
            else:
                p.setMatrix4('view', self.camera.view_matrix)
                p.setVec3f('viewPos', self.camera.position)

            for light in self.lights:
                light.update(p)

            self.model.draw(p)

    def dispose(self):
        super().dispose()
        if self.model is not None:
            self.model.dispose()


class TextureModel:

    ATTR_ORDER = [
        # 'position',
        # 'normal',
        'texcoords',
        'normal',
    ]

    def __init__(self,
                 name='',
                 vertices=None,
                 edges=None, faces=None,
                 attributes=None,
                 material=None):
        self.name = name
        self._vertices = None
        self._attrs = {}
        self._vertices_pending = None
        self._attrs_pending = None

        self._vertexobj = None
        self._indexobj_edges = None
        self._indexobj_faces = None

        self.vertices = vertices
        self.attrs = attributes
        self.material = material

        self._edges = edges
        self._faces = faces

    def prepare(self):
        if self._edges is not None and \
           self._indexobj_edges is None:
            self._indexobj_edges = IndexObject(self._edges)
        if self._faces is not None and \
           self._indexobj_faces is None:
            self._indexobj_faces = IndexObject(self._faces)

    def draw(self, program):
        self._update_geometry()

        if self._vertexobj is None:
            return

        with self.material(program):
            with self._vertexobj as vo:
                glPointSize(8)
                glDrawArrays(GL_POINTS, 0, vo.vertex_count)
                if self._indexobj_edges is not None:
                    with self._indexobj_edges as ebo:
                        glDrawElements(
                            GL_LINES,
                            ebo.count,
                            GL_UNSIGNED_SHORT,
                            None
                        )
                if self._indexobj_faces is not None:
                    with self._indexobj_faces as ebo:
                        glDrawElements(
                            GL_TRIANGLES,
                            ebo.count,
                            GL_UNSIGNED_SHORT,
                            None
                        )

    def dispose(self):
        self._indexobj_edges = None
        self._indexobj_faces = None

    def _update_geometry(self):
        if not self._check_pending_data():
            return

        v = self._build_data()

        if self._vertexobj is not None and \
           self._vertexobj.update(v):
            return

        self._vertexobj = VertexObject(
            v,
            self._alignment
        )

    def _check_pending_data(self):
        pending_check = self._vertices_pending is None and \
                        self._attrs_pending is None
        if pending_check:
            return False

        if self._vertices_pending is not None:
            self._vertices = self._vertices_pending
            self._vertices_pending = None

        # It does not make sense that color(or others) would be
        # updated without any vertices
        if self.vertices is None:
            return False

        if self._attrs_pending is not None:
            self._attrs = self._attrs_pending
            self._attrs_pending = None

        return True

    def _build_data(self):

        def _concat_withname(v, name):
            if name in self.attrs:
                return np.column_stack((v, self.attrs[name]))
            return v

        v = self.vertices
        if self.attrs is not None:
            for attr_name in self.ATTR_ORDER:
                # if attr_name == 'position':
                #     continue
                v = _concat_withname(v, attr_name)

        return v

    def _concat_withattrs(self, v, attrs):
        data = v
        for attr in attrs:
            data = np.column_stack((data, attr))
        return data

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, value):
        self._vertices_pending = value

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, value):
        self._attrs_pending = value

    @property
    def _alignment(self):
        a = [self.vertices.shape[1]]

        for attr_name in self.ATTR_ORDER:
            if attr_name in self.attrs:
                a.append(self.attrs[attr_name].shape[1])

        return a

    @property
    def use_material(self):
        return True
