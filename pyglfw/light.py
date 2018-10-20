import numpy as np


class DirectionalLight:

    def __init__(self,
                 name='dirLight',
                 direction=None,
                 ambient=None,
                 diffuse=None,
                 specular=None):
        zeros = np.zeros((3), dtype=np.float32)
        ones = np.ones((3), dtype=np.float32)

        self.direction = (direction, zeros)[direction is None]
        self.ambient = (ambient, zeros)[ambient is None]
        self.diffuse = (diffuse, ones)[diffuse is None]
        self.specular = (specular, zeros)[specular is None]

        self.name = name

    def update(self, program):
        program.setVec3f(self.name + '.direction', self.direction)
        program.setVec3f(self.name + '.ambient', self.ambient)
        program.setVec3f(self.name + '.diffuse', self.diffuse)
        program.setVec3f(self.name + '.specular', self.specular)
