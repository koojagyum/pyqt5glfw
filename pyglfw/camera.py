import math
import numpy as np
import pyrr


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class Camera:

    def __init__(self):
        self.position = np.array(
            [0.0, 0.0, 3.0],
            dtype=np.float32
        )
        self.world_up = np.array(
            [0.0, 1.0, 0.0],
            dtype=np.float32
        )
        self.yaw = math.radians(-90.0)
        self.pitch = math.radians(0.0)

        self.set_projection()

    def set_projection(
            self,
            fov=45.0,
            aspect_ratio=1.0/1.0,
            near_distance = 0.1,
            far_distance = 100.0):
        self._proj_matrix = pyrr.matrix44.create_perspective_projection(
            fov, aspect_ratio, near_distance, far_distance
        )

    @property
    def front(self):
        return np.array(
            [
                math.cos(self.yaw) * math.cos(self.pitch),
                math.sin(self.pitch),
                math.sin(self.yaw)
            ],
            dtype=np.float32
        )

    @property
    def right(self):
        return np.cross(self.front, self.world_up)

    @property
    def up(self):
        return np.cross(self.right, self.front)

    @property
    def view_matrix(self):
        target = self.position + self.front
        return pyrr.matrix44.create_look_at(
            self.position,
            target,
            self.up
        )

    @property
    def proj_matrix(self):
        return self._proj_matrix
