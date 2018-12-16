import sys

from OpenGL.GL import *
from PyQt5.QtWidgets import QApplication
from pyglfw.fbo import Framebuffer
from pyglfw.framework import VertexObject
from pyglfw.renderer import Renderer
from pyglfw.renderer import TriangleRenderer
from pyglfw.renderer import RectangleRenderer
from pyglfw.renderer import TextureRenderer
from pyqt5glfw.glwidget import GLWidget


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class FramebufferRenderer(TextureRenderer):

    def __init__(self, name=''):
        self._framebuffer = None
        self._inner_renderer = TriangleRenderer()
        super().__init__(name=name)

    def prepare(self):
        super().prepare()
        self._inner_renderer.prepare()
        self._framebuffer = Framebuffer(width=50, height=50)

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

    def setFramebufferSize(self, w=-1, h=-1):
        print('setFramebufferSize: {}, {}'.format(w, h))

        if w < 0:
            w = self._framebuffer.width
        if h < 0:
            h = self._framebuffer.height

        self._framebuffer.width = w
        self._framebuffer.height = h

    @property
    def texture(self):
        return self._framebuffer.texture


def test_fbo():
    app = QApplication(sys.argv)

    w = GLWidget()
    w.renderer = FramebufferRenderer()
    w.show()

    from PyQt5.QtCore import QTimer
    QTimer.singleShot(1000, lambda: w.renderer.setFramebufferSize(100, 100))
    QTimer.singleShot(1001, lambda: w.update())

    sys.exit(app.exec_())


if __name__ == '__main__':
    test_fbo()
