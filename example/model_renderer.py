import argparse
import sys

from pyglfw.model import load_fromjson
from pyglfw.renderer import ModelRenderer
from PyQt5.QtWidgets import QApplication
from pyqt5glfw.glwidget import GLWidget


verbose = False


def debug(msg):
    if verbose:
        print(msg)


def test_model_json(jsonpath):
    app = QApplication(sys.argv)

    w = GLWidget()
    model = load_fromjson(jsonpath)
    w.renderer = ModelRenderer(model=model)
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


if __name__ == '__main__':
    main()
