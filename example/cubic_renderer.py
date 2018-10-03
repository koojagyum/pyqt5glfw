import numpy as np
import random
import sys

from OpenGL.GL import *
from pyglfw.framework import VertexObject
from pyglfw.renderer import Renderer
from PyQt5.QtWidgets import QApplication
from pyqt5glfw.glwidget import GLWidget


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class CubicModel:
    cubic_vertices = np.array([
        [-0.5, -0.5, 0.99],
        [-0.5, +0.5, 0.01],
        [+0.5, +0.5, -0.99],
        [+0.5, -0.5, -1.000],
        [-0.5, -0.5, 3.5],
        [-0.5, +0.5, 3.5],
        [+0.5, +0.5, 3.5],
        [+0.5, -0.5, 3.5],
    ], dtype='float32')

    edges = [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [0, 4],
        [1, 5],
        [2, 6],
        [3, 7],
        [4, 5],
        [5, 6],
        [6, 7],
        [7, 4],
    ]

    def __init__(self, color=None):
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

        self.vertices = self.__class__.cubic_vertices

    def draw(self, program):
        self._update_geometry()

        if self._vertex_object is None:
            return

        with self._vertex_object as vo:
            print(vo.v_count)
            glPointSize(8)
            glDrawArrays(GL_POINTS, 0, vo.v_count)

    def _update_geometry(self):
        if not self._check_pending_data():
            return

        v = self._build_data()
        print(v)

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
        print(v)
        print(colors)
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


class CubicRenderer(Renderer):

    def __init__(self, name=''):
        super().__init__(
            name=name
        )
        self.model = CubicModel()

    def render(self):
        with self._program as p:
            self.model.draw(p)

    def dispose(self):
        super().dispose()
        self.model = None


def test_cubic_renderer():
    app = QApplication(sys.argv)

    w = GLWidget()
    w.renderer = CubicRenderer()
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    test_cubic_renderer()
