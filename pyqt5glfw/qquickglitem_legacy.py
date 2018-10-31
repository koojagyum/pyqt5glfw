import argparse
import sys

from OpenGL.GL import *

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickView
from PyQt5.QtQuick import QQuickItem
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import qmlRegisterType


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class QQuickGLItem(QQuickItem):

    keyPressed = pyqtSignal(int, bool)

    def __init__(self, parent=None):
        super(QQuickGLItem, self).__init__(
            parent=parent
        )

        self._renderer = None
        self._next_renderer = None

        self.windowChanged.connect(self._onWindowChanged)
        self.setProperty('focus', True)

        from pyglfw.scene import load_fromjson
        scene = load_fromjson('example/scene_cubicmat.json')
        self.keyPressed.connect(scene.camera.key_pressed)
        self.renderer = scene

    def _onWindowChanged(self, window):
        if window is not None:
            window.sceneGraphInitialized.connect(
                self.initializeUnderlay,
                type=Qt.DirectConnection
            )
            window.beforeSynchronizing.connect(
                self.synchronizeUnderlay,
                type=Qt.DirectConnection
            )
            window.beforeRendering.connect(
                self.renderUnderlay,
                type=Qt.DirectConnection
            )
            window.sceneGraphInvalidated.connect(
                self.invalidateUnderlay,
                type=Qt.DirectConnection
            )
            window.setClearBeforeRendering(False)

    def initializeUnderlay(self):
        self._check_next_renderer()

        if self._renderer:
            self._renderer.prepare()

        if self.window() is not None:
            self.window().resetOpenGLState()

    def invalidateUnderlay(self):
        if self._renderer:
            self._renderer.dispose()

        self.setProperty('focus', False)

        if self.window() is not None:
            self.window().resetOpenGLState()

    def renderUnderlay(self):
        # debug('color: {}'.format(self.color().getRgbF()))
        # glClearColor(
        #     self.color().getRgbF()[0],
        #     self.color().getRgbF()[1],
        #     self.color().getRgbF()[2],
        #     self.color().getRgbF()[3]
        # )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        switched = self._check_next_renderer()
        if self._renderer:
            if switched:
                self._renderer.prepare()
            glEnable(GL_CULL_FACE)
            self._renderer.render()

        if self.window() is not None:
            self.window().resetOpenGLState()

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
        super(QQuickGLItem, self).keyPressEvent(event)
        shift = event.modifiers() & Qt.ShiftModifier
        self.keyPressed.emit(event.key(), shift)
        self.update()

    def update(self):
        if self.window() is None:
            super(QQuickGLItem, self).update()
        else:
            self.window().update()

    @property
    def renderer(self):
        return self._renderer

    @renderer.setter
    def renderer(self, value):
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
