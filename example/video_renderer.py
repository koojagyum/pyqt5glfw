import cv2
import sys

from PyQt5.QtWidgets import QApplication
from pyglfw.renderer import TextureRenderer
from pyqt5glfw.glwidget import GLWidget
from utils.cvutils import Webcam, FPSChecker


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class VideoRenderer(TextureRenderer):

    def __init__(self,
                 name='',
                 image=None,
                 video_source=None,
                 frame_block=None):
        super().__init__(name=name, image=image)

        self.video_source = video_source
        self.fps_checker = FPSChecker()
        self.frame_block = frame_block

    def render(self):
        image = self.video_source.frame
        if image is not None:
            if self.frame_block:
                image = self.frame_block(image)
            self.fps_checker.lab(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image[::-1, ...]
            self.image = image

        super().render()


def test_webcam():
    app = QApplication(sys.argv)

    w = GLWidget()
    w.show()

    with Webcam() as webcam:
        def _block(frame):
            w.update()
            return frame

        w.renderer = VideoRenderer(
            video_source=webcam,
            frame_block=_block
        )

        sys.exit(app.exec_())


def test_livelm():
    app = QApplication(sys.argv)

    w = GLWidget()
    w.show()

    from facelm.detector import FaceDetector
    from utils.cvutils import Webcam

    with Webcam() as webcam:
        detector = FaceDetector()

        def draw_shape(image, shape, color=(255, 0, 0)):
            radius = 3
            for pt in shape:
                cv2.circle(image, (pt[0], pt[1]), radius, color, -1)

        def draw_shapes(image, shapes):
            for shape in shapes:
                draw_shape(image, shape)

        def _block(frame):
            _, shapes = detector.detect(frame)
            draw_shapes(frame, shapes)
            w.update()
            return frame

        w.renderer = VideoRenderer(
            video_source=webcam,
            frame_block=_block
        )

        sys.exit(app.exec_())


if __name__ == '__main__':
    # test_webcam()
    test_livelm()
