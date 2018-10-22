import json
import math
import numpy as np
import os
import sys

from .camera import Camera
from .instance import ModelInstance
from .light import load_light
from .model import load_model
from .rendererman import RendererManager

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
        resource_type = _pick(i, 'type')
        filepath = _pick(i, 'filepath')
        # todo: check ~ included path
        if os.path.isabs(filepath) is False:
            filepath = os.path.join(basepath, filepath)

        with open(filepath) as f:
            desc = json.load(f)

        if resource_type == 'model':
            model = load_model(desc, basepath)
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
        renderer_name = _pick(i, 'renderer')
        translation = _pick(i, 'translation')
        rotation = _pick(i, 'rotation')
        scale = _pick(i, 'scale')

        instance = ModelInstance(
            name=name,
            model=model,
            renderer_spec=renderer_name,
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


def load_lights(lights_desc):
    def _pick(dic, key):
        if key not in dic:
            return None
        return dic[key]

    def _pick_nparray(dic, key, dtype=np.float32):
        if key not in dic:
            return None
        return np.array(dic[key], dtype=dtype)

    light_list = []
    for desc in lights_desc:
        light = load_light(desc)
        if light is not None:
            light_list.append(light)

    return light_list


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

    debug(f'lights:\n{lights_desc}\n')
    light_list = load_lights(lights_desc)

    scene = Scene(
        name=name,
        camera=camera,
        instances=instance_list,
        lights=light_list
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
            camera=None,
            instances={},
            lights=[]):
        self._renderer_man = RendererManager()

        self.name = name
        self.camera = camera
        self.instances = instances
        self.lights = lights

        for i in self.instances.values():
            renderer = self._renderer_man.get_renderer(i.renderer_spec)
            renderer.instances.append(i)
            renderer.camera = self.camera
            renderer.lights = lights

    def prepare(self):
        for r in self._renderer_man.renderers:
            r.prepare()

    def reshape(self, w, h):
        glViewport(0, 0, w, h)
        for r in self._renderer_man.renderers:
            r.reshape(w, h)

    def render(self):
        for r in self._renderer_man.renderers:
            r.render()

    def dispose(self):
        for r in self._renderer_man.renderers:
            r.dispose()


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
