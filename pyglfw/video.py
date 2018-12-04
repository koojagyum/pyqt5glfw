import cv2
import numpy as np
import time

from threading import Thread
# Sync using Condition causes critical performance down
# from threading import Condition

from .renderer import TextureRenderer


class Webcam:

    def __init__(self):
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
        return _run

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


class VideoRenderer(TextureRenderer):

    def __init__(self,
                 name='',
                 image=None,
                 video_source=None,
                 frame_block=None):
        super().__init__(name=name, image=image)

        self.video_source = video_source
        self.frame_block = frame_block

    def render(self):
        image = self.video_source.frame
        if image is not None:
            if self.frame_block:
                image = self.frame_block(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image[::-1, ...]
            self.image = image

        super().render()
