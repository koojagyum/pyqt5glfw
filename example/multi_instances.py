import argparse
import math
import numpy as np
import sys

from pyglfw.model import load_fromjson
from pyglfw.model import InstanceRenderer
from pyglfw.model import ModelInstance
from PyQt5.QtWidgets import QApplication
from pyqt5glfw.glwidget import GLWidget


verbose = False


def debug(msg):
    if verbose:
        print(msg)


def test_json(jsonpath):
    app = QApplication(sys.argv)

    model = load_fromjson(jsonpath)
    instance1 = ModelInstance(
        name='instance1',
        model=model
    )
    instance2 = ModelInstance(
        name='instance1',
        model=model
    )
    instance1.translation = [3.0, 0.0, 1.0]
    instance1.scale = [2.0, 3.0, 3.0]
    instance1.rotation = [0.0, 0.0, 0.0]
    instance2.translation = [0.0, 0.0, 1.0]
    instance2.rotation = [30.0, 0.0, 0.0]

    renderer = InstanceRenderer()
    renderer.instances.append(instance1)
    renderer.instances.append(instance2)

    w = GLWidget()
    w.renderer = renderer
    w.keyPressed.connect(renderer.camera.key_pressed)
    w.show()

    renderer.camera.yaw = math.radians(90.0)
    renderer.camera.position = np.array([+3.0, 0.0, -10.0], dtype=np.float32)

    sys.exit(app.exec_())


def main():
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

    test_json(filepath)


if __name__ == '__main__':
    main()
