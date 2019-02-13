import math
import numpy as np

from pyglfw.camera import Camera


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class MouseCamera(Camera):

    def __init__(self, projection_type=None):
        super(MouseCamera, self).__init__(
            projection_type=projection_type
        )

        self._lpressed = False
        self._lastx = None
        self._lasty = None
        self._sensitivity = 0.005

    # Mouse events are delivered as following format
    # 1. (int) btn type: 1: left, 2: right, 3: middle
    # 2. (int) btn status: 1: press, 2: release, 0: move
    # 3,4 (int) position
    def mouse_event(self, btn, action, x, y):
        if btn == 1 and action == 1:
            self._lpressed = True

        if self._lpressed:
            self._process_mouse(x, y)

        if btn == 1 and action == 2:
            self._lpressed = False
            self._lastx = self._lasty = None

    def _process_mouse(self, x, y):
        if self._lastx is None or \
           self._lasty is None:
            self._lastx = x
            self._lasty = y

        xoffset = (x - self._lastx) * self._sensitivity
        # reversed since y-coordinates go from bottom to top
        yoffset = (self._lasty - y) * self._sensitivity

        self._lastx = x
        self._lasty = y

        self.yaw += xoffset
        self.pitch += yoffset

        with np.printoptions(precision=2, suppress=True):
            debug('Camera pos({}), yaw({:.2f}), pitch({:.2f})'.format(
                self.position,
                math.degrees(self.yaw),
                math.degrees(self.pitch)
            ))

    def dump_mouse(self, btn, action, x, y):
        btn_desc = ''
        ac_desc = ''

        if btn == 1:
            btn_desc = 'left'
        elif btn == 2:
            btn_desc = 'right'
        elif btn == 3:
            btn_desc = 'middle'

        if action == 0:
            ac_desc = 'move'
        elif action == 1:
            ac_desc = 'press'
        elif action == 2:
            ac_desc = 'release'

        debug('MOUSE: {}/{}, {},{}'.format(btn_desc, ac_desc, x, y))
