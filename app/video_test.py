import argparse
import numpy as np
import sys

from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQuick import QQuickView
from PyQt5.QtQml import qmlRegisterType

from .flip import FlipRenderer

from pyglfw.video import VideoPlayer
from pyglfw.video import VideoRenderer
from pyqt5glfw.qquickglitem import QQuickGLItem


class VideoView(QQuickGLItem):

    requestUpdate = pyqtSignal()

    def __init__(self, parent=None, play=False):
        super(VideoView, self).__init__(parent=parent)

        self._play = False
        self._videoSource = None
        self.player = VideoPlayer()

        video = VideoRenderer(
            video_source=self.player,
            frame_block=self._update_frame
        )
        # flip = FlipRenderer(
        #     width=self.player.width,
        #     height=self.player.height,
        #     inner_renderer=video
        # )
        flip = FlipRenderer(
            width=720,
            height=480,
            inner_renderer=video
        )

        self.renderer = video
        self.play = play

        self.requestUpdate.connect(self._requestUpdate)

    def __del__(self):
        self.play = False

    @pyqtProperty(bool)
    def play(self):
        return self._play

    @play.setter
    def play(self, value):
        if self._play != value:
            self._play = value
            if value:
                self.player.start()
            else:
                self.player.stop()

    @pyqtProperty(str)
    def videoSource(self):
        return self.player.srcpath

    @videoSource.setter
    def videoSource(self, value):
        if self.videoSource != value:
            self.player.srcpath = value

    # TODO: Add about resume
    def _onInvalidateUnderlay(self):
        super(VideoView, self)._onInvalidateUnderlay()
        self.play = False

    def _update_frame(self, image):
        self.requestUpdate.emit()
        return image

    def _requestUpdate(self):
        self.update()


def run_qml(qmlpath):
    app = QGuiApplication(sys.argv)

    qmlRegisterType(VideoView, 'PyQt5GLfwTest', 1, 0, 'VideoView')

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setSource(QUrl(qmlpath))
    view.show()

    sys.exit(app.exec_())


def main():
    global verbose

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
        help='Print debug string'
    )

    args = parser.parse_args()
    verbose = args.verbose

    run_qml('qml/video_test.qml')


if __name__ == '__main__':
    main()
