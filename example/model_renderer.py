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


def test_model_json(jsonpath):
    app = QApplication(sys.argv)

    model = load_fromjson(jsonpath)
    renderer = ModelRenderer(model=model)
    renderer.camera.yaw = math.radians(90.0)
    renderer.camera.position = np.array([0.0, 0.0, -1.0], dtype=np.float32)

    w = GLWidget()
    w.renderer = renderer
    w.keyPressed.connect(renderer.camera.key_pressed)
    w.show()

    # from PyQt5.QtCore import QTimer

    # def _change1():
    #     model.color = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    #     w.update()

    # def _change2():
    #     model.color = np.array([1.0, 1.0, 0.0], dtype=np.float32)
    #     w.update()

    # def _change3():
    #     model.color = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    #     w.update()

    # QTimer.singleShot(1000, lambda: _change1())
    # QTimer.singleShot(2000, lambda: _change2())
    # QTimer.singleShot(3000, lambda: _change3())

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

    test_model_json(filepath)


if __name__ == '__main__':
    main()
