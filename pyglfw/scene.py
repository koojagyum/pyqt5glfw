import json
import numpy as np

from .camera import Camera
from OpenGL.GL import *
from .renderer import *


def load_fromjson(jsonpath):
    with open(jsonpath) as f:
        desc = json.load(f)


class Scene:

    def __init__(
            self, name='scene',
            models=[],
            light=None):
        pass
