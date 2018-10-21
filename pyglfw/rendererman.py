import sys

from .renderer import *
from .model import ModelRenderer
from .instance import InstanceRenderer
from .instance import MonoInstanceRenderer


def _class_ofname(classname):
    return getattr(sys.modules[__name__], classname)


class RendererManager:

    def __init__(self):
        self._renderer_map = {}

    def _register_renderer(self, name):
        class_functor = _class_ofname(name)
        self._renderer_map[name] = class_functor(name=name)

    def get_renderer(self, name):
        if name not in self._renderer_map:
            self._register_renderer(name)

        if name in self._renderer_map:
            return self._renderer_map[name]

        return None

    def dispose(self, name):
        if name in self._renderer_map:
            self._renderer_map.pop(name, None)

    def dispose_all(self):
        self._renderer_map = {}

    @property
    def renderers(self):
        return self._renderer_map.values()
