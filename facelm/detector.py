import argparse
import cv2
import dlib
import math
import numpy as np
import os
import random
import sys

from . import downloader

from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib import patheffects
from threading import Timer


verbose = False


def debug(msg):
    if verbose:
        print(msg)


class FaceDetector:

    def __init__(self, resize_width=512):
        predictor_path = downloader.check_model()
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)
        self.width = int(resize_width)

    def get_landmarks(self, image, bboxes):
        landmarks = np.array(
            [[[p.x, p.y]
              for p in self.predictor(image, bb).parts()]
             for bb in bboxes]
        )
        return landmarks

    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        width = min(self.width, image.shape[1])
        scale = width / image.shape[1]
        dsize = (width, int(image.shape[0] * scale))
        gray = cv2.resize(gray, dsize=dsize)

        rects = self.detector(gray, 1)
        landmarks = self.get_landmarks(gray, rects)

        for (i, rect) in enumerate(rects):
            left = int(rect.left() / scale)
            top = int(rect.top() / scale)
            right = int(rect.right() / scale)
            bottom = int(rect.bottom() / scale)
            rects[i] = dlib.rectangle(left, top, right, bottom)

        divisor = 1.0 / scale
        for (i, shape) in enumerate(landmarks):
            shape = (shape * divisor).astype(dtype=np.int32)
            landmarks[i] = shape

        self.rects = rects
        self.landmarks = landmarks
        return self.rects, self.landmarks


def plot_shapes(image, shapes):
    fig, ax = plt.subplots()

    ax.imshow(image)
    for (i, shape) in enumerate(shapes):
        color_spec = 'C{}'.format(i)
        ax.plot(
            shape[:, 0],
            shape[:, 1],
            color=color_spec,
            marker='.',
            linestyle='None'
        )
        debug(shape)

    plt.show()


def plot_bboxes(image, bboxes):
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(111)
    plt.imshow(image)

    for bb in bboxes:
        x = bb.left()
        y = bb.top()
        w = bb.right() - x
        h = bb.bottom() - y
        ax1.add_patch(
            patches.Rectangle(
                (x, y),
                w, h,
                fill=False,
                edgecolor='#00ff00'
            )
        )

    plt.show()


def plot_lmindices(img, shape):
    '''Plot for a single shape'''

    fig, ax = plt.subplots()

    ax.imshow(img)
    ax.scatter(shape[:, 0], shape[:, 1], s=10, color='blue', edgecolor='black')

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


def test_bbox(image_path):
    detector = FaceDetector()
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    rects, _ = detector.detect(image)

    plot_bboxes(image, rects)


def test_shape(image_path):
    detector = FaceDetector()
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    _, shapes = detector.detect(image)

    plot_shapes(image, shapes)


def test_lmindices(image_path):
    detector = FaceDetector()
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    _, shapes = detector.detect(image)

    plot_lmindices(image, shapes[0])


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
        '--input', '-i',
        required=True,
        help='Path for input file'
    )

    args = parser.parse_args()
    verbose = args.verbose
    input_path = args.input

    debug(' - input_path: {}'.format(input_path))
    input_path = os.path.expanduser(input_path)

    # test_bbox(input_path)
    # test_shape(input_path)
    test_lmindices(input_path)


if __name__ == '__main__':
    main()
