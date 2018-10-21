import argparse
import math
import numpy as np
import sys

from pyglfw.camera import Camera
from pyglfw.instance import ModelInstance
from pyglfw.instance import MonoInstanceRenderer
from pyglfw.light import DirectionalLight
from pyglfw.model import load_fromjson
from pyglfw.model import ModelRenderer
from PyQt5.QtWidgets import QApplication
from pyqt5glfw.glwidget import GLWidget


verbose = False


def debug(msg):
    if verbose:
        print(msg)


def test_model_light(jsonpath):
    app = QApplication(sys.argv)

    model = load_fromjson(jsonpath)
    light = DirectionalLight(
        direction=np.array([-0.2, -0.1, -0.3], dtype=np.float32)
    )

    renderer = ModelRenderer(model=model, camera=Camera(), lights=[light])
    renderer.camera.yaw = math.radians(240.0)
    renderer.camera.pitch = math.radians(-18.0)
    renderer.camera.position = np.array([1.0, 1.0, 1.8], dtype=np.float32)

    w = GLWidget()
    w.renderer = renderer
    w.keyPressed.connect(renderer.camera.key_pressed)
    w.show()

    sys.exit(app.exec_())


def test_model_mono(jsonpath):
    app = QApplication(sys.argv)

    model = load_fromjson(jsonpath)
    instance = ModelInstance(model=model)

    renderer = MonoInstanceRenderer(camera=Camera())
    renderer.instances.append(instance)
    renderer.camera.yaw = math.radians(240.0)
    renderer.camera.pitch = math.radians(-18.0)
    renderer.camera.position = np.array([1.0, 1.0, 1.8], dtype=np.float32)

    w = GLWidget()
    w.renderer = renderer
    w.keyPressed.connect(renderer.camera.key_pressed)
    w.show()

    sys.exit(app.exec_())


def test_model_attr(jsonpath):
    app = QApplication(sys.argv)

    model = load_fromjson(jsonpath)
    renderer = ModelRenderer(model=model, camera=Camera())
    renderer.camera.yaw = math.radians(90.0)
    renderer.camera.position = np.array([0.0, 0.0, -1.0], dtype=np.float32)

    w = GLWidget()
    w.renderer = renderer
    w.show()

    from PyQt5.QtCore import QTimer

    def _change1():
        model.color = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        w.update()

    def _change2():
        model.color = np.array([1.0, 1.0, 0.0], dtype=np.float32)
        w.update()

    def _change3():
        model.color = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        w.update()

    QTimer.singleShot(1000, lambda: _change1())
    QTimer.singleShot(2000, lambda: _change2())
    QTimer.singleShot(3000, lambda: _change3())

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
    parser.add_argument(
        '--mono', '-m',
        action='store_true',
        default=False,
        help='Whether using mono renderer or directional light'
    )

    args = parser.parse_args()

    verbose = args.verbose
    filepath = args.filepath
    use_mono = args.mono

    if use_mono:
        test_model_mono(filepath)
    else:
        test_model_light(filepath)


if __name__ == '__main__':
    main()
