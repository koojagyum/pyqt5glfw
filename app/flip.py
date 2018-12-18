import numpy as np


from OpenGL.GL import *

from pyglfw.fbo import Framebuffer
from pyglfw.framework import VertexObject
from pyglfw.renderer import TextureRenderer


class FlipRenderer(TextureRenderer):

    def __init__(
            self,
            name='',
            width=100,
            height=100,
            inner_renderer=None):
        self._pending_width = -1
        self._pending_height = -1
        self._width = 0
        self._height = 0
        self._framebuffer = None

        self.width = width
        self.height = height
        self._inner_renderer = inner_renderer

        super().__init__(name=name)

    def prepare(self):
        super().prepare()
        v = np.array(
            [-1.0, -1.0, +0.0, 1.0, 0.0,
             +1.0, -1.0, +0.0, 0.0, 0.0,
             -1.0, +1.0, +0.0, 1.0, 1.0,
             +1.0, +1.0, +0.0, 0.0, 1.0],
            dtype='float32'
        )
        e = np.array(
            [0, 1, 2,
             1, 3, 2],
            dtype='uint8'
        )
        self._vertexobj = VertexObject(v, [3, 2], e)

        self._inner_renderer.prepare()

    def render(self):
        self._check_size()
        if self._framebuffer is None:
            return

        with self._framebuffer:
            glClearColor(0.0, 0.0, 0.0, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self._inner_renderer.render()

        super().render()

    def dispose(self):
        super().dispose()

        self._pending_width = self._width
        self._pending_height = self._height
        self._width = self._height = -1

        self._framebuffer = None
        self._inner_renderer.dispose()

    def _check_size(self):
        if self._pending_width < 0 and \
           self._pending_height < 0:
            return False

        if self._pending_width >= 0:
            self._width = self._pending_width
        if self._pending_height >= 0:
            self._height = self._pending_height
        self._pending_width = self._pending_height = -1

        if self._framebuffer is None:
            self._framebuffer = Framebuffer(width=self.width, height=self.height)
        else:
            self._framebuffer.width = self.width
            self._framebuffer.height = self.height

        return True

    @property
    def texture(self):
        return self._framebuffer.texture

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if self.width != value:
            self._pending_width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if self.height != value:
            self._pending_height = value
