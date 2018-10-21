import json
import numpy as np
import pyrr

from .camera import Camera
from .light import DirectionalLight
from .model import Model
from .renderer import Renderer
from .renderer import resource_path

from OpenGL.GL import *
from pyglfw.framework import IndexObject
from pyglfw.framework import VertexObject


verbose = True


def debug(msg):
    if verbose:
        print(msg)


class ModelInstance:

    def __init__(
            self, name='',
            model=None,
            translation=[0.0, 0.0, 0.0],
            rotation=[0.0, 0.0, 0.0],
            scale=[1.0, 1.0, 1.0]):
        self.name = name
        self.model = model
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

    def prepare(self):
        if self.model:
            self.model.prepare()

    def draw(self, program):
        if self.model:
            program.setMatrix4('model', self.model_matrix)
            self.model.draw(program)

    def dispose(self):
        if self.model:
            self.model.dispose()

    @property
    def model_matrix(self):
        scale_mat = pyrr.matrix44.create_from_scale(
            np.array(self.scale, dtype=np.float32)
        )
        trans_mat = pyrr.matrix44.create_from_translation(
            np.array(self.translation, dtype=np.float32)
        )
        rot_mat = pyrr.matrix44.create_from_eulers(
            np.radians(np.array(self.rotation, dtype=np.float32))
        )
        return np.matmul(rot_mat, np.matmul(scale_mat, trans_mat))


class InstanceRenderer(Renderer):

    default_vs_path = resource_path('./shader/model_color_light.vs')
    default_fs_path = resource_path('./shader/model_color_light.fs')

    def __init__(self, name='', camera=None, light=None):
        super().__init__(
            vs_path=self.default_vs_path,
            fs_path=self.default_fs_path,
            name=name
        )
        self.instances = []
        self.camera = camera
        self.light = DirectionalLight(
            name='dirLight',
            direction=np.array([-0.2, -0.1, -0.3], dtype=np.float32)
        )

    def prepare(self):
        super().prepare()
        with self._program as p:
            if self.camera is None:
                p.setMatrix4(
                    'projection',
                    pyrr.matrix44.create_identity()
                )
            else:
                p.setMatrix4('projection', self.camera.proj_matrix)

        for i in self.instances:
            i.prepare()

    def render(self):
        if len(self.instances) == 0:
            return

        with self._program as p:
            if self.camera is None:
                p.setMatrix4('view', pyrr.matrix44.create_identity())
            else:
                p.setMatrix4('view', self.camera.view_matrix)
                p.setVec3f('viewPos', self.camera.position)

            if self.light is not None:
                self.light.update(p)

            for i in self.instances:
                i.draw(p)

    def dispose(self):
        super().dispose()
        for i in self.instances:
            i.dispose()
