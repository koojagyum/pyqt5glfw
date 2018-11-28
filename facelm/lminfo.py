import argparse
import cv2
import json
import numpy as np
import os

from .detector import FaceDetector

verbose = False


def debug(msg):
    if verbose:
        print(msg)


def _to_ndc(vert, res=(1.0, 1.0), inverty=True):
    vert_ndc = vert.copy()

    modifier = (1.0, -1.0)[inverty]
    vert_ndc[:,0] = vert_ndc[:,0] * 2.0 / res[0] - 1.0
    vert_ndc[:,1] = (vert_ndc[:,1] * 2.0 / res[1] - 1.0) * modifier

    return vert_ndc


def _plot_lm_ndc(lm):
    from matplotlib import pyplot as plt
    from matplotlib import patches
    from matplotlib import patheffects

    fig, ax = plt.subplots()
    shape = lm

    ax.scatter(shape[:, 0], shape[:, 1], s=10, color='blue', edgecolor='black')
    ax.set_xlim([-1.0, 1.0])
    ax.set_ylim([-1.0, 1.0])

    for i in range(shape.shape[0]):
        txt = ax.text(
            shape[i, 0],
            shape[i, 1],
            str(i),
            fontsize=10,
            color='white'
        )
        txt.set_path_effects([patheffects.withStroke(linewidth=1, foreground='black')])

    plt.show()


def load_lminfo_fromjson(jsonfile):
    def _pick(key, dic, default=None):
        if key not in dic:
            return default
        return dic[key]

    with open(jsonfile) as f:
        lminfo_desc = json.load(f)

    name = _pick('name', lminfo_desc)
    imgpath = _pick('imgpath', lminfo_desc)
    v_lm = _pick('vert_lm', lminfo_desc)
    v_lm = np.array(v_lm)
    lmtype = _pick('lmtype', lminfo_desc, 'dlib')

    return LmInfo(name=name, v_lm=v_lm, imgpath=imgpath, lmtype=lmtype)


def load_lminfo_fromimg(imgfile):
    name = os.path.splitext(os.path.basename(imgfile))[0]
    jsonfile = os.path.splitext(imgfile)[0] + '.json'

    detector = FaceDetector()
    img = cv2.imread(imgfile)
    _, shapes = detector.detect(img)
    v_lm = _to_ndc(shapes[0].astype(np.float32), (img.shape[1], img.shape[0]))

    return LmInfo(name=name, v_lm=v_lm, imgpath=imgfile, lmtype='dlib')


class LmInfo:

    def __init__(
            self,
            name=None,
            v_lm=[],
            imgpath=None,
            lmtype='dlib'):
        self.name = name
        self.v_lm = v_lm
        self.imgpath = imgpath
        self.lmtype = lmtype

    def write(self, outfile):
        with open(outfile, 'w') as f:
            json.dump(self.data, f, indent=2)

    @property
    def data(self):
        data = {
            'name': self.name,
            'imgpath': self.imgpath,
            'lmtype': self.lmtype,
            'vert_lm': self.v_lm.tolist()
        }
        return data

    def __str__(self):
        return str(self.data)


def test_write_json(imgfile, jsonfile):
    lminfo = load_lminfo_fromimg(imgfile)
    lminfo.write(jsonfile)
    print(lminfo)


def test_read_json(jsonfile):
    lminfo = load_lminfo_fromjson(jsonfile)
    print(lminfo)

    _plot_lm_ndc(lminfo.v_lm)


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
        '--imgfile', '-i',
        required=True,
        help='Input image file path'
    )
    parser.add_argument(
        '--outfile', '-o',
        required=True,
        help='Output JSON file path'
    )

    args = parser.parse_args()

    verbose = args.verbose
    imgfile = args.imgfile
    outfile = args.outfile

    test_write_json(imgfile, outfile)
    test_read_json(outfile)


if __name__ == '__main__':
    main()
