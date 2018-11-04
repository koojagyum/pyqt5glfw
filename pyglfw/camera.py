import math
import numpy as np
import pyrr

from PyQt5.QtCore import Qt


verbose = True


def debug(msg):
    if verbose:
        print(msg)


def load_camera(camera_dic):
    def _pick(dic, key):
        if key not in dic:
            return None
        return dic[key]

    position = _pick(camera_dic, 'position')
    up = _pick(camera_dic, 'up')
    rotation = _pick(camera_dic, 'rotation')
    projection_type = _pick(camera_dic, 'type')

    fov = _pick(camera_dic, 'fov')
    aspect_ratio = _pick(camera_dic, 'aspect_ratio')
    near_distance = _pick(camera_dic, 'near_distance')
    far_distance = _pick(camera_dic, 'far_distance')

    move_speed = _pick(camera_dic, 'move_speed')

    camera = Camera(projection_type=projection_type)
    camera.position = np.array(position, dtype=np.float32)
    camera.world_up = np.array(up, dtype=np.float32)
    camera.yaw = math.radians(rotation[0])
    camera.pitch = math.radians(rotation[1])
    camera.set_projection(
        fov=fov,
        aspect_ratio=aspect_ratio,
        near_distance=near_distance,
        far_distance=far_distance
    )
    if move_speed is not None:
        camera.SPEED = move_speed

    return camera


class Camera:

    PITCH = math.radians(0.0)
    YAW = math.radians(-90.0)
    SPEED = 3.0 * 0.1
    SPEED_ROTATION = math.radians(3.0)

    def __init__(self, projection_type=None):
        self.position = np.array(
            [0.0, 0.0, 3.0],
            dtype=np.float32
        )
        self.world_up = np.array(
            [0.0, 1.0, 0.0],
            dtype=np.float32
        )
        self.yaw = Camera.YAW
        self.pitch = Camera.PITCH
        if projection_type is None:
            projection_type = 'perspective'
        self.projection_type = projection_type

        self.set_projection()

    def set_projection(
            self,
            fov=45.0,
            aspect_ratio=1.0/1.0,
            near_distance = 0.1,
            far_distance = 100.0):
        if self.projection_type == 'perspective':
            self._proj_matrix = pyrr.matrix44.create_perspective_projection(
                fov, aspect_ratio, near_distance, far_distance
            )
        elif self.projection_type == 'orthographic':
            self._proj_matrix = pyrr.matrix44.create_orthogonal_projection(
                -1.0, 1.0, -1.0, 1.0, 0.1, 100.0
            )
        else:
            self._proj_matrix = pyrr.matrix44.create_identity()

    def key_pressed(self, key, shift):
        if not shift:
            if key == Qt.Key_A:
                self.position -= self.right * self.SPEED
            elif key == Qt.Key_D:
                self.position += self.right * self.SPEED
            elif key == Qt.Key_S:
                self.position -= self.front * self.SPEED
            elif key == Qt.Key_W:
                self.position += self.front * self.SPEED
        else:
            if key == Qt.Key_A:
                self.yaw += self.SPEED_ROTATION
            elif key == Qt.Key_D:
                self.yaw -= self.SPEED_ROTATION
            elif key == Qt.Key_S:
                self.pitch -= self.SPEED_ROTATION
            elif key == Qt.Key_W:
                self.pitch += self.SPEED_ROTATION

        with np.printoptions(precision=2, suppress=True):
            debug('Camera pos({}), yaw({:.2f}), pitch({:.2f})'.format(
                self.position,
                math.degrees(self.yaw),
                math.degrees(self.pitch)
            ))

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
