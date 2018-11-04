import argparse
import sys

from OpenGL.GL import *

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat
from PyQt5.QtQuick import QQuickView
from PyQt5.QtQuick import QQuickFramebufferObject
from PyQt5.QtQml import qmlRegisterType

from pyglfw.renderer import RendererBase


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class QQuickGLItem(QQuickFramebufferObject):

    keyPressed = pyqtSignal(int, bool)

    def __init__(self, parent=None):
        super(QQuickGLItem, self).__init__(
            parent=parent
        )

        self.renderer = None
        self._qrenderer = None
        self.windowChanged.connect(self._onWindowChanged)
        self.setProperty('focus', True)
        self.setProperty('mirrorVertically', True)

        # from pyglfw.scene import load_fromjson
        # scene = load_fromjson('example/res/scene_rectangle.json')
        # self.keyPressed.connect(scene.camera.key_pressed)
        # self.renderer = scene

    def createRenderer(self):
        self._qrenderer = QQuickRenderer()
        return self._qrenderer

    def keyPressEvent(self, event):
        super(QQuickGLItem, self).keyPressEvent(event)
        shift = event.modifiers() & Qt.ShiftModifier
        self.keyPressed.emit(event.key(), shift)
        self.update()

    def _onWindowChanged(self, window):
        if window is not None:
            window.sceneGraphInvalidated.connect(
                self._onInvalidateUnderlay,
                type=Qt.DirectConnection
            )

    def _onInvalidateUnderlay(self):
        self.setProperty('focus', False)


class QQuickRenderer(QQuickFramebufferObject.Renderer):

    def __init__(self):
        super(QQuickRenderer, self).__init__()

        self._qfbo = None
        self._window = None
        self._renderer = None
        self._next_renderer = None

    def render(self):
        # todo: specify color
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        switched = self._check_next_renderer()
        if self._renderer is not None:
            if switched:
                self._renderer.prepare()
            glEnable(GL_CULL_FACE)
            self._renderer.render()

        if self._window is not None:
            self._window.resetOpenGLState()

    def createFramebufferObject(self, size):
        format = QOpenGLFramebufferObjectFormat()
        format.setAttachment(
            QOpenGLFramebufferObject.CombinedDepthStencil
        )
        format.setSamples(4)

        self._qfbo = QOpenGLFramebufferObject(size, format)
        return self._qfbo

    def synchronize(self, item):
        # update data from main thread
        self._window = item.window()
        self.renderer = item.renderer

    def _check_next_renderer(self):
        switched = self._next_renderer is not None
        if switched:
            if self._renderer:
                self._renderer.dispose()

            self._renderer = self._next_renderer
            self._next_renderer = None

        return switched

    @property
    def renderer(self):
        return self._renderer

    @renderer.setter
    def renderer(self, value):
        if self._next_renderer != value:
            if value is not None and \
               not isinstance(value, RendererBase):
                print(value)
                raise TypeError

            self._next_renderer = value
            self.update()


def run_qml(qmlpath):
    app = QGuiApplication(sys.argv)
    qmlRegisterType(QQuickGLItem, 'GLItem', 1, 0, 'GLItem')

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setSource(QUrl(qmlpath))
    view.show()

    sys.exit(app.exec_())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
        help='Print debug strings'
    )
    args = parser.parse_args()
    verbose = args.verbose

    run_qml('qml/test_glitem.qml')


if __name__ == '__main__':
    main()
