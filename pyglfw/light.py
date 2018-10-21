import numpy as np


def load_light(desc):
    def _pick(dic, key, default=None):
        if key not in dic:
            return default
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
    elif class_name == 'PointLight':
        print(desc)
        position = _pick_nparray(desc, 'position')
        ambient = _pick_nparray(desc, 'ambient')
        diffuse = _pick_nparray(desc, 'diffuse')
        specular = _pick_nparray(desc, 'specular')

        constant = _pick(desc, 'constant', 0.0)
        linear = _pick(desc, 'linear', 0.0)
        quadratic = _pick(desc, 'quadratic', 0.0)

        return PointLight(
            name=name,
            position=position,
            ambient=ambient,
            diffuse=diffuse,
            specular=specular,
            constant=constant,
            linear=linear,
            quadratic=quadratic
        )

    return None


class Light:

    def __init__(self,
                 name='light',
                 ambient=None,
                 diffuse=None,
                 specular=None):
        zeros = np.zeros((3), dtype=np.float32)
        ones = np.ones((3), dtype=np.float32)

        self.ambient = (ambient, zeros)[ambient is None]
        self.diffuse = (diffuse, ones)[diffuse is None]
        self.specular = (specular, zeros)[specular is None]

        self.name = name

    def update(self, program):
        program.setVec3f(self.name + '.ambient', self.ambient)
        program.setVec3f(self.name + '.diffuse', self.diffuse)
        program.setVec3f(self.name + '.specular', self.specular)


class DirectionalLight(Light):

    def __init__(self,
                 name='dirLight',
                 direction=None,
                 ambient=None,
                 diffuse=None,
                 specular=None):
        super().__init__(
            name=name,
            ambient=ambient,
            diffuse=diffuse,
            specular=specular
        )

        zeros = np.zeros((3), dtype=np.float32)
        self.direction = (direction, zeros)[direction is None]

    def update(self, program):
        super().update(program)
        program.setVec3f(self.name + '.direction', self.direction)


class PointLight(Light):

    def __init__(self,
                 name='pointLight',
                 position=None,
                 ambient=None,
                 diffuse=None,
                 specular=None,
                 constant=0.0,
                 linear=0.0,
                 quadratic=0.0):
        super().__init__(
            name=name,
            ambient=ambient,
            diffuse=diffuse,
            specular=specular
        )

        zeros = np.zeros((3), dtype=np.float32)
        self.position = (position, zeros)[position is None]

        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic

    def update(self, program):
        super().update(program)

        program.setVec3f(self.name + '.position', self.position)
        program.setFloat(self.name + '.constant', self.constant)
        program.setFloat(self.name + '.linear', self.linear)
        program.setFloat(self.name + '.quadratic', self.quadratic)
