import argparse
import math
import numpy as np
import sys

from pyglfw.model import load_fromjson
from pyglfw.model import ModelRenderer
from PyQt5.QtWidgets import QApplication
from pyqt5glfw.glwidget import GLWidget


verbose = False


def debug(msg):
    if verbose:
        print(msg)


def test_json(jsonpath):
    pass
