import json
import numpy as np
import pyrr
import random

from .camera import Camera
from .light import DirectionalLight
from .renderer import Renderer
from .renderer import resource_path

from OpenGL.GL import *
from pyglfw.framework import IndexObject
from pyglfw.framework import VertexObject


verbose = True


def debug(msg):
    if verbose:
        print(msg)


def load_model(desc):
    def _pick(key, dic, dtype=np.float32):
        if key not in dic:
            return None
        return np.asarray(dic[key], dtype=dtype)

    vertices = _pick('vertices', desc, dtype=np.float32)
    edges = _pick('edges', desc, dtype=np.uint8)
    faces = _pick('faces', desc, dtype=np.uint8)
    color = _pick('color', desc, dtype=np.float32)

    attrs = None
    key_attr = 'attributes'
    if key_attr in desc:
        attrs = desc[key_attr]
        for key, value in attrs.items():
            attrs[key] = np.array(value, dtype=np.float32)

    name = None
    if 'name' in desc:
        name = desc['name']

    return Model(
        name=name,
        vertices=vertices,
        edges=edges,
        faces=faces,
        color=color,
        attributes=attrs
    )


def load_fromjson(jsonpath):
    with open(jsonpath) as f:
        desc = json.load(f)
        return load_model(desc)

    return None


class Model:

    ATTR_ORDER = [
        # 'position',
        'color',
        'normal',
    ]

    def __init__(self,
                 name='',
                 vertices=None,
                 edges=None, faces=None,
                 color=None, attributes=None):
        self.name = name
        self._vertices = None
        self._color = None
        self._attrs = {}
        self._vertices_pending = None
        self._color_pending = None
        self._attrs_pending = None

        self._vertexobj = None
        self._indexobj_edges = None
        self._indexobj_faces = None

        self.draw_mode = 'points'

        self.vertices = vertices
        self.attrs = attributes

        if color is None and \
           'color' not in attributes:
            color = (
                random.random(),
                random.random(),
                random.random()
            )
        self.color = color

        self._edges = edges
        self._faces = faces

    def prepare(self):
        if self._edges is not None:
            self._indexobj_edges = IndexObject(self._edges)
        if self._faces is not None:
            self._indexobj_faces = IndexObject(self._faces)

    def draw(self, program):
        self._update_geometry()

        if self._vertexobj is None:
            return

        with self._vertexobj as vo:
            glPointSize(8)
            glDrawArrays(GL_POINTS, 0, vo.vertex_count)
            if self._indexobj_edges is not None:
                with self._indexobj_edges as ebo:
                    glDrawElements(
                        GL_LINES,
                        ebo.count,
                        GL_UNSIGNED_BYTE,
                        None
                    )
            if self._indexobj_faces is not None:
                with self._indexobj_faces as ebo:
                    glDrawElements(
                        GL_TRIANGLES,
                        ebo.count,
                        GL_UNSIGNED_BYTE,
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


class ModelInstance:

    def __init__(
            self, name='',
            model=None,
            translation=[0.0, 0.0, 0.0],
            rotation=[0.0, 0.0, 0.0],
            scale=[1.0, 1.0, 1.0]):
        self.name = name
        self.model = model
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

    def prepare(self):
        if self.model:
            self.model.prepare()

    def draw(self, program):
        if self.model:
            program.setMatrix4('model', self.model_matrix)
            self.model.draw(program)

    def dispose(self):
        if self.model:
            self.model.dispose()

    @property
    def model_matrix(self):
        scale_mat = pyrr.matrix44.create_from_scale(
            np.array(self.scale, dtype=np.float32)
        )
        trans_mat = pyrr.matrix44.create_from_translation(
            np.array(self.translation, dtype=np.float32)
        )
        rot_mat = pyrr.matrix44.create_from_eulers(
            np.radians(np.array(self.rotation, dtype=np.float32))
        )
        return np.matmul(rot_mat, np.matmul(scale_mat, trans_mat))


class InstanceRenderer(Renderer):

    default_vs_path = resource_path('./shader/model_color_light.vs')
    default_fs_path = resource_path('./shader/model_color_light.fs')

    def __init__(self, name='', camera=None, light=None):
        super().__init__(
            vs_path=self.default_vs_path,
            fs_path=self.default_fs_path,
            name=name
        )
        self.instances = []
        self.camera = camera
        self.light = DirectionalLight(
            name='dirLight',
            direction=np.array([-0.2, -0.1, -0.3], dtype=np.float32)
        )

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

        for i in self.instances:
            i.prepare()

    def render(self):
        if len(self.instances) == 0:
            return

        with self._program as p:
            if self.camera is None:
                p.setMatrix4('view', pyrr.matrix44.create_identity())
            else:
                p.setMatrix4('view', self.camera.view_matrix)
                p.setVec3f('viewPos', self.camera.position)

            if self.light is not None:
                self.light.update(p)

            for i in self.instances:
                i.draw(p)

    def dispose(self):
        super().dispose()
        for i in self.instances:
            i.dispose()


class ModelRenderer(Renderer):

    default_vs_path = resource_path('./shader/model_color_light.vs')
    default_fs_path = resource_path('./shader/model_color_light.fs')

    def __init__(self, name='', model=None, camera=None):
        super().__init__(
            vs_path=self.default_vs_path,
            fs_path=self.default_fs_path,
            name=name
        )
        self.model = model
        self.camera = camera
        self.light = DirectionalLight(
            name='dirLight',
            direction=np.array([-0.2, -0.1, -0.3], dtype=np.float32)
        )

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

            if self.light is not None:
                self.light.update(p)

            self.model.draw(p)

    def dispose(self):
        super().dispose()
        if self.model is not None:
            self.model.dispose()
