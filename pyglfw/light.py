import numpy as np


def load_light(desc):
    def _pick(dic, key):
        if key not in dic:
            return None
        return dic[key]

    def _pick_nparray(dic, key, dtype=np.float32):
        if key not in dic:
            return None
        return np.array(dic[key], dtype=dtype)

    name = _pick(desc, 'name')
    class_name = _pick(desc, 'class')

    if class_name == 'DirectionalLight':
        direction = _pick_nparray(desc, 'direction')
        ambient = _pick_nparray(desc, 'ambient')
        diffuse = _pick_nparray(desc, 'diffuse')
        specular = _pick_nparray(desc, 'specular')

        return DirectionalLight(
            name=name,
            direction=direction,
            ambient=ambient,
            diffuse=diffuse,
            specular=specular
        )

    return None


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
