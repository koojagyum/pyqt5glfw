import cv2
import numpy as np
import time

from threading import Thread
from threading import Condition
# Sync using Condition causes critical performance down
# from threading import Condition

from .renderer import TextureRenderer


class FrameProvider:

    def __init__(self, srcpath=None):
        self._img = None
        self._srcpath = None

        self.srcpath = srcpath

    def _load(self):
        self._img = cv2.imread(self._srcpath)

    @property
    def frame(self):
        return self._img

    @property
    def srcpath(self):
        return self._srcpath

    @srcpath.setter
    def srcpath(self, value):
        if self._srcpath != value:
            self._srcpath = value
            self._load()

    @property
    def width(self):
        if self._img is not None:
            return self._img.shape[0]
        return 0.0

    @property
    def height(self):
        if self._img is not None:
            return self._img.shape[1]
        return 0.0

    @property
    def aspect_ratio(self):
        if self._img is not None:
            return self._img.shape[0] / self._img.shape[1]
        # Invalid case
        return 0.0


class Webcam:

    def __init__(self):
        self._img = None
        self._cap = None
        self._cap_cond = Condition()

        self._load()

    def _load(self):
        with self._cap_cond as cond:
            self._cap = cv2.VideoCapture(0)
            __, self._img = self._cap.read()
            self._cap_cond.notifyAll()

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
        if self._cap is None:
            with self._cap_cond as cond:
                self._cap_cond.wait()

        while self._run:
            succeed, temp_frame = self._cap.read()
            if succeed:
                self._img = temp_frame
            self._run = self._run and succeed

    @property
    def frame(self):
        # Copy may cause some problems about performance
        # return self._img
        return np.copy(self._img)

    @property
    def run(self):
        return _run

    @property
    def width(self):
        return self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    @property
    def height(self):
        return self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    @property
    def aspect_ratio(self):
        return float(self.height) / float(self.width)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.stop()

    def __del__(self):
        self.stop()
        self._cap.release()


class VideoPlayer(Webcam):

    def __init__(self, srcpath=None):
        self._img = None
        self._srcpath = None
        self._cap = None
        self._cap_cond = Condition()

        self.srcpath = srcpath

    def _load(self):
        if self.srcpath is not None:
            with self._cap_cond as cond:
                self._cap = cv2.VideoCapture(self.srcpath)
                __, self._img = self._cap.read()
                self._cap_cond.notifyAll()

    @property
    def srcpath(self):
        return self._srcpath

    @srcpath.setter
    def srcpath(self, value):
        if self._srcpath != value:
            self._srcpath = value
            self._load()


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
