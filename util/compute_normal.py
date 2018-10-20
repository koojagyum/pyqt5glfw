import json
import numpy as np
import os
import sys


from pyglfw.model import load_model


verbose = True


def debug(msg):
    if verbose:
        print(msg)


def test_json(jsonpath):
    with open(jsonpath) as f:
        desc = json.load(f)

    def _pick(dic, key, dtype=np.float32):
        if key not in dic:
            return None
        return np.asarray(dic[key], dtype=dtype)

    vertices = _pick(desc, 'vertices', dtype=np.float32)
    faces = _pick(desc, 'faces', dtype=np.uint8)

    normals = np.zeros(vertices.shape, dtype=np.float32)
    for face in faces:
        v = vertices[face[0:3]]
        n = np.cross(v[0] - v[1], v[0] - v[2])
        n = n / np.linalg.norm(n)
        normals[face[0:3]] = n

    for n in normals:
        print(f'[{n[0]}, {n[1]}, {n[2]}],')


def main():
    import argparse
    import sys

    global verbose

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=False,
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
