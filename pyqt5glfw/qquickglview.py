import argparse
import sys

from OpenGL.GL import *

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QApplication


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class QQuickGLView(QQuickView):

    keyPressed = pyqtSignal(int, bool)

    def __init__(self, parent=None):
        super(QQuickView, self).__init__(parent)

        self._renderer = None
        self._next_renderer = None

        self.sceneGraphInitialized.connect(
            self.initializeUnderlay,
            type=Qt.DirectConnection
        )
        self.beforeSynchronizing.connect(
            self.synchronizeUnderlay,
            type=Qt.DirectConnection
        )
        self.beforeRendering.connect(
            self.renderUnderlay,
            type=Qt.DirectConnection
        )
        self.sceneGraphInvalidated.connect(
            self.invalidateUnderlay,
            type=Qt.DirectConnection
        )

        self.setClearBeforeRendering(False)
        self.setColor(QColor.fromRgbF(0.0, 0.0, 0.0))

    def initializeUnderlay(self):
        self._check_next_renderer()

        if self._renderer:
            self._renderer.prepare()

        self.resetOpenGLState()

    def invalidateUnderlay(self):
        if self._renderer:
            self._renderer.dispose()

        self.resetOpenGLState()

    def renderUnderlay(self):
        debug('color: {}'.format(self.color().getRgbF()))
        glClearColor(
            self.color().getRgbF()[0],
            self.color().getRgbF()[1],
            self.color().getRgbF()[2],
            self.color().getRgbF()[3]
        )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        switched = self._check_next_renderer()
        if self._renderer:
            if switched:
                self._renderer.prepare()
            glEnable(GL_CULL_FACE)
            self._renderer.render()

        self.resetOpenGLState()

    def synchronizeUnderlay(self):
        pass

    def _check_next_renderer(self):
        switched = self._next_renderer is not None
        if switched:
            if self._renderer:
                self._renderer.dispose()

            self._renderer = self._next_renderer
            self._next_renderer = None

        return switched

    def keyPressEvent(self, event):
        super(QQuickGLView, self).keyPressEvent(event)
        shift = event.modifiers() & Qt.ShiftModifier
        self.keyPressed.emit(event.key(), shift)
        self.update()

    @property
    def renderer(self):
        return self._renderer

    @renderer.setter
    def renderer(self, value):
        self._next_renderer = value
        self.update()


def test_switching():
    app = QApplication(sys.argv)

    v = QQuickGLView()
    v.show()

    from PyQt5.QtCore import QTimer
    from pyglfw.renderer import TriangleRenderer
    from pyglfw.renderer import RectangleRenderer

    def _change_renderer(view, renderer):
        debug('change_renderer: {}'.format(renderer))
        view.renderer = renderer

    QTimer.singleShot(1000, lambda: _change_renderer(v, TriangleRenderer()))
    QTimer.singleShot(2000, lambda: _change_renderer(v, RectangleRenderer()))
    QTimer.singleShot(3000, lambda: _change_renderer(v, TriangleRenderer()))
    QTimer.singleShot(4000, lambda: _change_renderer(v, RectangleRenderer()))

    sys.exit(app.exec_())


def test_qquickglview():
    from pyglfw.renderer import TriangleRenderer

    app = QApplication(sys.argv)

    view = QQuickGLView()
    view.show()

    view.renderer = TriangleRenderer()

    sys.exit(app.exec_())


def test_qquickview():
    app = QApplication(sys.argv)

    view = QQuickView()
    view.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
        help='Print debug strings'
    )
    args = parser.parse_args()
    verbose = args.verbose

    # test_qquickglview()
    test_switching()
