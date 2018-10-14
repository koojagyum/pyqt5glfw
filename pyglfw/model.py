import json
import numpy as np
import pyrr
import random

from .camera import Camera
from OpenGL.GL import *
from pyglfw.framework import IndexObject
from pyglfw.framework import VertexObject
from .renderer import Renderer
from .renderer import resource_path


verbose = True


def debug(msg):
    if verbose:
        print(msg)


def load_fromjson(jsonpath):
    with open(jsonpath) as f:
        desc = json.load(f)

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

    return Model(
        vertices=vertices,
        edges=edges,
        faces=faces,
        color=color,
        attributes=attrs
    )


class Model:

    def __init__(self,
                 vertices=None,
                 edges=None, faces=None,
                 color=None, attributes=None):
        self._vertices = None
        self._color = None
        self._attrs = None
        self._vertices_pending = None
        self._color_pending = None
        self._attrs_pending = None

        self._vertex_object = None
        self._indexobj_edges = None
        self._indexobj_faces = None

        self.draw_mode = 'points'

        self.vertices = vertices
        self.attrs = attributes

        if color is None and attributes is None:
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

        if self._vertex_object is None:
            return

        with self._vertex_object as vo:
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

    def _update_geometry(self):
        if not self._check_pending_data():
            return

        v = self._build_data()

        if self._vertex_object is not None and \
           self._vertex_object.update(v):
            return

        self._vertex_object = VertexObject(
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
        if self.color is not None:
            return self._concat_withcolors(self.vertices)
        else:
            return self._concat_withattrs(
                self.vertices,
                self.attrs.values()
            )

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
        if value is not None:
            self._attrs_pending = None

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, value):
        self._attrs_pending = value
        if value is not None:
            self._color_pending = None

    @property
    def _alignment(self):
        if self.color is not None:
            return [self.vertices.shape[1], 3]

        a = [self.vertices.shape[1]]
        for v in self.attrs.values():
            a.append(v.shape[1])

        return a


class ModelRenderer(Renderer):

    default_vs_path = resource_path('./shader/model_color.vs')
    default_fs_path = resource_path('./shader/model_color.fs')

    def __init__(self, name='', model=None):
        super().__init__(
            vs_path=self.default_vs_path,
            fs_path=self.default_fs_path,
            name=name
        )
        self.model = model
        self.camera = Camera()

    def prepare(self):
        super().prepare()
        with self._program as p:
            p.setMatrix4('projection', self.camera.proj_matrix)

        if self.model is not None:
            self.model.prepare()

    def render(self):
        if self.model is None:
            return

        with self._program as p:
            p.setMatrix4('view', self.camera.view_matrix)
            self.model.draw(p)

    def dispose(self):
        super().dispose()
