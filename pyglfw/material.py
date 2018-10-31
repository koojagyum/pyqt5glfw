import argparse
import cv2
import json
import os
import sys

from .framework import Program
from .framework import Texture

from OpenGL.GL import *


verbose = False


def debug(msg):
    if verbose:
        print(msg)


def load_material(desc, basepath='.'):
    def _pick(dic, key, default=None):
        if key not in dic:
            return default
        return dic[key]

    def _pick_path(dic, key, default=None):
        if key not in dic:
            return default
        return os.path.join(basepath, dic[key])

    name = _pick(desc, 'name')
    diffuse_path = _pick_path(desc, 'diffuse')
    specular_path = _pick_path(desc, 'specular')
    normal_path = _pick_path(desc, 'normal')
    depth_path = _pick_path(desc, 'depth')
    shininess = _pick(desc, 'shininess', 1.0)

    debug(f'name: {name}')
    debug(f'diffuse_path: {diffuse_path}')
    debug(f'specular_path: {specular_path}')
    debug(f'normal_path: {normal_path}')
    debug(f'depth_path: {depth_path}')

    material = Material(name=name)
    material.shininess = shininess

    def _add_image(name, imgpath, to):
        if imgpath is not None:
            img = cv2.imread(imgpath)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            to.add_image(name, img)

    _add_image('diffuse', diffuse_path, material)
    _add_image('specular', specular_path, material)
    _add_image('normal', normal_path, material)
    _add_image('depth', depth_path, material)

    return material


def load_fromjson(jsonpath):
    with open(jsonpath) as f:
        desc = json.load(f)
        basepath = os.path.dirname(jsonpath)
        return load_material(desc, basepath)

    return None


class Material:

    def __init__(self, name='material', textures={}):
        self.name = name
        self.textures = {}
        self._images_pending = {}
        self._program = None
        self.shininess = 1.0

    def __call__(self, program):
        self._program = program
        return self

    def __enter__(self):
        # todo
        # we should check other texture bindings of texture targets
        # currently only dealing with GL_TEXTURE_2D
        self._prev_texid = glGetIntegerv(GL_TEXTURE_BINDING_2D)
        self._prev_texunit =  glGetIntegerv(GL_ACTIVE_TEXTURE)
        self.update(self._program)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.restore()
        glActiveTexture(self._prev_texunit)
        glBindTexture(GL_TEXTURE_2D, self._prev_texid)

    def _update_textures(self):
        for name, image in self._images_pending.items():
            unit = GL_TEXTURE0
            for t in self.textures.values():
                if unit != t.unit:
                    break
                unit += 1
            self.textures[name] = Texture(
                image=image,
                unit=unit
            )
            debug(f'_update_textures ({name}) to slot ({unit})')

        self._images_pending = {}

    def add_image(self, name, image):
        self._images_pending[name] = image

    def dispose_image(self, name):
        self.textures.pop(name, None)

    def dispose_all(self):
        self.textures = {}

    def update(self, program):
        self._update_textures()
        for texname, tex in self.textures.items():
            tex.bind()
            program.setInt(self.name + '.' + texname, tex.unit_number)

        program.setFloat(self.name + '.' + 'shininess', self.shininess)

    def restore(self):
        for texname, tex in self.textures.items():
            tex.unbind()


def main():
    global verbose

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
        help='Print debug string'
    )
    parser.add_argument(
        '--filepath', '-f',
        required=True,
        help='Model JSON file path'
    )

    args = parser.parse_args()

    verbose = args.verbose
    filepath = args.filepath

    load_fromjson(filepath)


if __name__ == '__main__':
    main()
