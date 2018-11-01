import argparse
import math
import numpy as np
import sys

from pyglfw.camera import Camera
from pyglfw.model import load_fromjson
from pyglfw.model import ModelRenderer
from PyQt5.QtWidgets import QApplication
from pyqt5glfw.qquickglview import QQuickGLView


verbose = False


def debug(msg):
    if verbose:
        print(msg)


def test_model_json(jsonpath):
    model = load_fromjson(jsonpath)

    app = QApplication(sys.argv)

    renderer = ModelRenderer(model=model, camera=Camera())
    renderer.camera.yaw = math.radians(90.0)
    renderer.camera.position = np.array([0.0, 0.0, -1.0], dtype=np.float32)

    w = QQuickGLView()
    w.renderer = renderer
    w.keyPressed.connect(renderer.camera.key_pressed)
    w.show()

    sys.exit(app.exec_())


def test_model_textbook(jsonpath):
    frame_size = (640, 480)
    model = load_fromjson(jsonpath)

    app = QApplication(sys.argv)

    renderer = ModelRenderer(model=model)
    renderer.camera.yaw = math.radians(-90.0)
    renderer.camera.position = np.array(
        [57.0, 41.0, 247.0], dtype=np.float32
    )
    renderer.camera.SPEED = 3.0
    renderer.camera.set_projection(
        aspect_ratio=frame_size[0]/frame_size[1],
        far_distance=1000.0,
        near_distance=0.1
    )

    w = QQuickGLView()
    w.renderer = renderer
    w.keyPressed.connect(renderer.camera.key_pressed)
    w.show()

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
    # test_model_textbook(filepath)


if __name__ == '__main__':
    main()
