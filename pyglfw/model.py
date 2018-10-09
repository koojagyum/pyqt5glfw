import json
import numpy as np

from OpenGL.GL import *
from pyglfw.framework import VertexObject


verbose = True


def debug(msg):
    if verbose:
        print(msg)


def load_fromjson(jsonpath):
    with open(jsonpath) as f:
        desc = json.load(f)

    vertices = desc['vertices']
    vertices = np.asarray(vertices, dtype=np.float32)

    edges = desc['edges']
    edges = np.asarray(edges, dtype=np.int32)

    color = desc['color']
    color = np.asarray(color, dtype=np.float32)

    return Model(vertices=vertices, edges=edges, color=color)


class Model:

    def __init__(self,
                 vertices=None, edges=None, color=None):
        self._vertices = None
        self._vertices_pending = None
        self._color_pending = None

        if color is None:
            color = (
                random.random(),
                random.random(),
                random.random()
            )
        self.color = color

        self._vertex_object = None
        self.draw_mode = 'points'

        self.vertices = vertices

    def draw(self, program):
        self._update_geometry()

        if self._vertex_object is None:
            return

        with self._vertex_object as vo:
            glPointSize(8)
            glDrawArrays(GL_POINTS, 0, vo.v_count)

    def _update_geometry(self):
        if not self._check_pending_data():
            return

        v = self._build_data()

        if self._vertex_object is None:
            self._vertex_object = VertexObject(
                v,
                self._alignment
            )
        else:
            self._vertex_object.update(v)

    def _check_pending_data(self):
        if self._vertices_pending is None and \
           self._color_pending is None:
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

        return True

    def _build_data(self):
        v = self._concat_withcolors(self.vertices)
        return v

    def _get_colors(self, num):
        color = np.array((self.color), dtype='float32')
        colors = np.tile(color, num).reshape((num, 3))
        return colors

    def _concat_withcolors(self, v):
        num = v.shape[0]
        colors = self._get_colors(num)
        return np.column_stack((v, colors))

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

    @property
    def _alignment(self):
        a = [3, 3]
        return a
