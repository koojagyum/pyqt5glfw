import json
import math
import numpy as np
import os
import sys

from .camera import Camera
from .model import load_model
from .model import InstanceRenderer
from .model import ModelInstance
from .renderer import *

from OpenGL.GL import *
from PyQt5.QtWidgets import QApplication
from pyqt5glfw.glwidget import GLWidget


verbose = False


def debug(msg):
    if verbose:
        print(msg)


def load_resources(resources_dic, basepath='.'):
    def _pick(dic, key):
        if key not in dic:
            return None
        return dic[key]

    resource_list = {}
    model_list = {}

    for i in resources_dic:
        name = _pick(i, 'name')
        filepath = _pick(i, 'filepath')
        # todo: check ~ included path
        if os.path.isabs(filepath) is False:
            filepath = os.path.join(basepath, filepath)

        with open(filepath) as f:
            desc = json.load(f)

        if name == 'model':
            model = load_model(desc)
            model_list[model.name] = model

    resource_list['model'] = model_list

    return resource_list


def load_instance(instances_dic, model_list):
    def _pick(dic, key):
        if key not in dic:
            return None
        return dic[key]

    instance_list = {}

    for i in instances_dic:
        name = _pick(i, 'name')
        model = None
        model_name = _pick(i, 'model')
        if model_name in model_list:
            model = model_list[model_name]
        # renderer_name = _pick(i, 'renderer')
        # renderer = globals()[renderer_name]
        # print(renderer)
        translation = _pick(i, 'translation')
        rotation = _pick(i, 'rotation')
        scale = _pick(i, 'scale')

        instance = ModelInstance(
            name=name,
            model=model,
            translation=translation,
            rotation=rotation,
            scale=scale
        )
        instance_list[name] = instance

    return instance_list


def load_camera(camera_dic):
    def _pick(dic, key):
        if key not in dic:
            return None
        return dic[key]

    position = _pick(camera_dic, 'position')
    up = _pick(camera_dic, 'up')
    rotation = _pick(camera_dic, 'rotation')
    fov = _pick(camera_dic, 'fov')
    aspect_ratio = _pick(camera_dic, 'aspect_ratio')
    near_distance = _pick(camera_dic, 'near_distance')
    far_distance = _pick(camera_dic, 'far_distance')
    move_speed = _pick(camera_dic, 'move_speed')

    camera = Camera()
    camera.position = position
    camera.world_up = up
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


def load_fromjson(jsonpath):
    with open(jsonpath) as f:
        desc = json.load(f)

    def _pick(dic, key):
        if key not in dic:
            return None
        return dic[key]

    name = _pick(desc, 'name')
    resources_desc = _pick(desc, 'resources')
    lights_desc = _pick(desc, 'lights')
    instances_desc = _pick(desc, 'instances')
    camera_desc = _pick(desc, 'camera')

    basepath = os.path.dirname(jsonpath)

    debug(f'name: {name}')

    resource_list = load_resources(
        resources_desc,
        basepath
    )
    debug(f'resources:\n{resource_list}\n')

    instance_list = load_instance(
        instances_desc,
        resource_list['model']
    )
    debug(f'instances:\n{instance_list}\n')

    camera = load_camera(camera_desc)
    debug(f'camera: {camera}\n')

    renderer = InstanceRenderer()
    for i in instance_list.values():
        renderer.instances.append(i)

    scene = Scene(
        name=name,
        renderer=renderer,
        camera=camera,
        instances=instance_list
    )
    debug(f'scene: {scene}\n')

    return scene


def test_json(jsonpath):
    scene = load_fromjson(jsonpath)

    app = QApplication(sys.argv)
    w = GLWidget()
    w.renderer = scene
    w.keyPressed.connect(scene.camera.key_pressed)
    w.show()

    sys.exit(app.exec_())


class Scene:

    def __init__(
            self,
            name='scene',
            renderer=None,
            camera=None,
            instances={},
            lights=[]):
        self.name = name
        self.renderer = renderer
        self.camera = camera
        self.instances = instances
        self.lights = lights

        self.renderer.camera = camera

    def prepare(self):
        if self.renderer is not None:
            self.renderer.prepare()

    def render(self):
        if self.renderer is not None:
            self.renderer.render()

    def dispose(self):
        if self.renderer is not None:
            self.renderer.dispose()


def main():
    import argparse
    import sys

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

    test_json(filepath)


if __name__ == '__main__':
    main()
