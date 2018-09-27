import argparse
import pyglfw
import OpenGL.GL as gl
import sys

from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QOpenGLWidget, QWidget


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class GLWidget(QOpenGLWidget):

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.lastPos = QPoint()
        self._renderer = None
        self._next_renderer = None

    def getOpenglInfo(self):
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
        """.format(
            gl.glGetString(gl.GL_VENDOR),
            gl.glGetString(gl.GL_RENDERER),
            gl.glGetString(gl.GL_VERSION),
            gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        )

        return info

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def initializeGL(self):
        debug(self.getOpenglInfo())

        self.setClearColor(QColor.fromRgbF(0.0, 0.0, 0.0, 1.0))

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

        if self._renderer:
            self._renderer.prepare()

    def paintGL(self):
        gl.glClear(
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT
        )

        if self._next_renderer:
            if self._renderer:
                self._renderer.dispose()

            self._renderer = self._next_renderer
            if self._renderer:
                self._renderer.prepare()

            self._next_renderer = None

        if self._renderer:
            self._renderer.render()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport(
            (width - side) // 2,
            (height - side) // 2,
            side, side
        )

    def mousePressEvent(self, event):
        self.lastPos = event.pos()
        debug(self.lastPos)

    def mouseMoveEvent(self, event):
        self.lastPos = event.pos()

    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    @property
    def renderer(self):
        return self._renderer

    @renderer.setter
    def renderer(self, value):
        self._next_renderer = value
        self.update()

    def closeEvent(self, event):
        debug('closeEvent')
        self._renderer = None


def test_widget():
    app = QApplication(sys.argv)

    w = GLWidget()
    w.show()

    from pyglfw.renderer import TriangleRenderer
    w.renderer = TriangleRenderer()

    sys.exit(app.exec_())


def test_switching():
    app = QApplication(sys.argv)

    w = GLWidget()
    w.show()

    from PyQt5.QtCore import QTimer
    from pyglfw.renderer import TriangleRenderer
    from pyglfw.renderer import RectangleRenderer

    def _change_renderer(widget, renderer):
        widget.renderer = renderer

    QTimer.singleShot(1000, lambda: _change_renderer(w, TriangleRenderer()))
    QTimer.singleShot(2000, lambda: _change_renderer(w, RectangleRenderer()))
    QTimer.singleShot(3000, lambda: _change_renderer(w, TriangleRenderer()))
    QTimer.singleShot(4000, lambda: _change_renderer(w, RectangleRenderer()))

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

    # test_widget()
    test_switching()
