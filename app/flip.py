import numpy as np


from OpenGL.GL import *

from pyglfw.framework import Framebuffer
from pyglfw.framework import VertexObject
from pyglfw.renderer import TextureRenderer


class FlipRenderer(TextureRenderer):

    def __init__(
            self,
            name='',
            width=100,
            height=100,
            inner_renderer=None):
        self._width = width
        self._height = height
        self._framebuffer = None
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
        self._framebuffer = Framebuffer(width=self.width, height=self.height)

    def render(self):
        with self._framebuffer:
            glClearColor(0.0, 0.0, 0.0, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self._inner_renderer.render()

        super().render()

    def dispose(self):
        super().dispose()
        self._framebuffer = None
        self._inner_renderer.dispose()

    @property
    def texture(self):
        return self._framebuffer.texture

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if self.width != value:
            self._width = value
            # todo: update_framebuffer

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if self.height != value:
            self._height = value
            # todo: update_framebuffer
