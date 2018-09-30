import cv2
import numpy as np
import time

from threading import Thread
# Sync using Condition causes critical performance down
# from threading import Condition


class Webcam:

    def __init__(self):
        self._run = False
        self._cap = cv2.VideoCapture(0)
        __, self._frame = self._cap.read()

    # Create thread for capturing image
    def start(self):
        self._run = True
        self._thread = Thread(
            target=self._update_frame,
            args=()
        )
        self._thread.start()

    def stop(self):
        self._run = False
        self._thread.join()

    def _update_frame(self):
        while self._run:
            succeed, temp_frame = self._cap.read()
            if succeed:
                self._frame = temp_frame
            self._run = self._run and succeed

    @property
    def frame(self):
        # Copy may cause some problems about performance
        # return self._frame
        return np.copy(self._frame)

    @property
    def run(self):
        return self._run

    @property
    def width(self):
        return self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    @property
    def height(self):
        return self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.stop()

    def __del__(self):
        self.stop()
        self._cap.release()


class FPSChecker:

    def __init__(self):
        self.fps = 0

        self._timeToCheck = time.time()
        self._frameCount = 0

        self.color = (0, 0, 255)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.pos = (0, 30)
        self.interval = 1.0

    def draw(self, frame):
        format_ = '{:5.2f} fps'.format(self.fps)
        if len(frame.shape) < 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        cv2.putText(
            frame,
            format_,
            self.pos,
            self.font,
            1,
            self.color,
            1,
            cv2.LINE_AA
        )

        return frame

    def lab(self, frame=None):
        now = time.time()
        dt = now - self._timeToCheck
        self._frameCount += 1
        if dt > self.interval:
            self.fps = float(self._frameCount) / dt

            self._frameCount = 0
            self._timeToCheck = now

        if frame is not None:
            self.draw(frame)

        return self.fps


def test_webcam():
    from .detector import FaceDetector

    detector = FaceDetector()
    fps_checker = FPSChecker()

    def _draw_bbox(image, bb, color=(0, 255, 0)):
        left = bb.left()
        top = bb.top()
        right = bb.right()
        bottom = bb.bottom()

        cv2.rectangle(
            image,
            (left, top),
            (right, bottom),
            color=color,
            thickness=2
        )

    def _draw_bboxes(image, bboxes):
        color = (0, 255, 0)

        for bb in bboxes:
            _draw_bbox(image, bb, color)

    def _draw_shape(image, shape, color=(255, 0, 0)):
        radius = 3
        for pt in shape:
            cv2.circle(image, (pt[0], pt[1]), radius, color, -1)

    def _draw_shapes(image, shapes):
        for shape in shapes:
            _draw_shape(image, shape)

    def _block(frame):
        rects, shapes = detector.detect(frame)
        if len(rects) > 0:
            _draw_bboxes(frame, rects)
            _draw_shapes(frame, shapes)
        return frame

    with Webcam() as video:
        title = 'webcam test'
        while True:
            frame = video.frame
            fps_checker.lab(frame)

            frame = _block(frame)
            cv2.imshow(title, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # When everything done, release the capture
    cv2.destroyAllWindows()


if __name__ == '__main__':
    test_webcam()
