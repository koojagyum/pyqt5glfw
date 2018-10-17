import json
import numpy as np
import os

from .camera import Camera
from .model import load_model
from .model import InstanceRenderer
from .model import ModelInstance
from OpenGL.GL import *
from .renderer import *


def load_resources(resources_dic, basepath='.'):
    def _pick(dic, key):
        if key not in dic:
            return None
        return dic[key]

    resource_list = {}

    for i in resources_dic:
        name = _pick(i, 'name')
        filepath = _pick(i, 'filepath')
        # todo: check ~ included path
        if os.path.isabs(filepath) is False:
            filepath = os.path.join(basepath, filepath)

        with open(filepath) as f:
            desc = json.load(f)

        model_list = {}
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
    return None


def load_fromjson(jsonpath):
    with open(jsonpath) as f:
        desc = json.load(f)

    def _pick(dic, key):
        if key not in dic:
            return None
        return dic[key]

    name = _pick(desc, 'name')
    resources = _pick(desc, 'resources')
    lights = _pick(desc, 'lights')
    instances = _pick(desc, 'instances')
    camera = _pick(desc, 'camera')

    basepath = os.path.dirname(jsonpath)

    # print(name)
    # print(resource)
    # print(light)
    # print(instance)
    # print(camera)

    resource_list = load_resources(resources, basepath)
    print('resources:')
    print(resource_list)
    print('')

    instance_list = load_instance(instances, resource_list['model'])
    print('instances:')
    print(instance_list)
    print('')


class Scene:

    def __init__(
            self, name='scene',
            models=[],
            light=None):
        pass


def main():
    import argparse
    import sys

    global verbose

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=True,
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
