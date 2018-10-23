import sys

from .renderer import *
from .model import ModelRenderer
from .instance import InstanceRenderer
from .instance import MonoInstanceRenderer


def _class_ofname(classname):
    return getattr(sys.modules[__name__], classname)


def serialize_spec(spec):
    def _pick(key, dic, default=None):
        if key not in dic:
            return default
        return dic[key]

    classname = _pick('class', spec, '')
    params = _pick('params', spec, {})

    serialized = classname + '.'
    for key, value in params.items():
        serialized += key + '=' + str(value) + ','

    return serialized[:-1]


class RendererManager:

    def __init__(self):
        self._renderer_map = {}

    def _register_renderer(self, key, spec):
        classname = spec['class']
        params = spec['params']
        class_functor = _class_ofname(classname)
        self._renderer_map[key] = class_functor(**params)

    def get_renderer(self, spec):
        key = serialize_spec(spec)

        if key not in self._renderer_map:
            self._register_renderer(key, spec)

        if key in self._renderer_map:
            return self._renderer_map[key]

        return None

    def dispose(self, key):
        if key in self._renderer_map:
            self._renderer_map.pop(key, None)

    def dispose_all(self):
        self._renderer_map = {}

    @property
    def renderers(self):
        return self._renderer_map.values()
