import argparse
import cv2
import glob
import math
import numpy as np
import os

from .detector import FaceDetector
from utils.filesys import filename_of
from utils.filesys import mkdirp

verbose = False


def debug(msg):
    if verbose:
        print(msg)


def correct_roll(image, shape):
    angle_ignore = 0

    def _unit(v):
        """Returns the unit vector of the vector."""
        return v / np.linalg.norm(v)

    def _angle(v1, v2):
        """Returns the angle in radians between vectors"""
        return np.math.atan2(np.linalg.det([v1, v2]), np.dot(v1, v2))

    # Select the first face
    lm = shape

    v_eyes = lm[16] - lm[0]
    v_eyes = v_eyes.astype(np.float32)

    v_h = np.array([1.0, 0.0], lm.dtype)
    v_h = v_h.astype(np.float32)

    mid_eyes = (lm[45] + lm[36]) * 0.5
    angle_eyes = np.degrees(_angle(v_eyes, v_h))
    # debug('angle_eyes: {}'.format(angle_eyes))
    if abs(angle_eyes) <= abs(angle_ignore):
        # debug('discard rotation')
        return image, mid_eyes

    m = cv2.getRotationMatrix2D(
        tuple(mid_eyes),
        -angle_eyes,
        1
    )
    rotated = cv2.warpAffine(image, m, (image.shape[1::-1]))

    return rotated, mid_eyes


def _rotate_and_crop(image, shape):
    lm = shape
    rotated, center = correct_roll(image, lm)

    v = center - lm[8]
    dist_input = math.hypot(v[0], v[1])
    dist_h = int(dist_input / 1.3)
    dist_v = int(dist_input / 0.9)

    # normalize image -----
    # lm30(코 랜드마크) 기준으로 crop 센터를 맞추고
    # lm19,lm24중점과 lm8거리를 가지고 crop 영역을 정함
    # cropped image를 scale해서 일정 크기 이미지로 맞춤
    # lm30 -> lm29로 바꿈 -> center로 바꿈
    # center = lm[27]  # lm[29]

    src_sx = max(int(center[0] - dist_h), 0)
    src_ex = min(int(center[0] + dist_h), rotated.shape[1])
    src_sy = max(int(center[1] - dist_v), 0)
    src_ey = min(int(center[1] + dist_v), rotated.shape[0])

    crop_width = src_ex - src_sx
    crop_height = src_ey - src_sy

    crop_sx = int((dist_h * 2 - crop_width) / 2)
    crop_ex = int(crop_sx + crop_width)
    crop_sy = int((dist_v * 2 - crop_height) / 2)
    crop_ey = int(crop_sy + crop_height)

    rgb_crop = np.zeros((dist_v * 2, dist_h * 2, 3), np.uint8)
    rgb_crop[:] = 127

    slice_dv = slice(crop_sy, crop_ey)
    slice_dh = slice(crop_sx, crop_ex)
    slice_sv = slice(src_sy, src_ey)
    slice_sh = slice(src_sx, src_ex)

    rgb_crop[slice_dv, slice_dh] = rotated[slice_sv, slice_sh]
    # rgb_crop_resize = cv2.resize(rgb_crop, (200, 200))
    # gray = cv2.cvtColor(rgb_crop, cv2.COLOR_BGR2GRAY)

    return rgb_crop


def make_squared(image):
    height, width = image.shape[:2]

    if (width != height):
        size = max(width, height)
        squared = np.zeros((size, size, 3), np.uint8)
        squared[:] = 127

        def _range(x):
            return int((size - x) / 2), int(size - (size - x) / 2)

        r_range = _range(height)
        c_range = _range(width)
        squared[r_range[0]:r_range[1], c_range[0]:c_range[1]] = image

        return squared

    return image


def crop(image):
    squared = make_squared(image)
    detector = FaceDetector()
    _, shapes = detector.detect(squared)

    cropped_list = []
    for shape in shapes:
        cropped = _rotate_and_crop(squared, shape)
        cropped_list.append(cropped)

    return cropped_list


def process_crop(indir, outdir):
    mkdirp(outdir)

    imgfiles = glob.glob(os.path.join(indir, '*g'))
    for f in imgfiles:
        filename = filename_of(f)
        debug('Processing {} ...'.format(filename))

        img = cv2.imread(f)
        if img is None:
            debug('Error: Failed to read {} as image'.format(filename_of(f)))
            continue
        cropped_list = crop(img)
        name, _ = os.path.splitext(filename)
        ext = '.jpg'

        i = 1
        for cropped in cropped_list:
            outname = name + '_' + str(i) + ext
            outpath = os.path.join(outdir, outname)
            cv2.imwrite(outpath, cropped)
            i += 1
    debug('** process_crop Done')


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
        '--indir', '-i',
        required=True,
        help='Source folder of images'
    )
    parser.add_argument(
        '--outdir', '-o',
        required=True,
        help='Output folder images cropped'
    )

    args = parser.parse_args()

    verbose = args.verbose
    indir = args.indir
    outdir = args.outdir

    print('Start')
    process_crop(indir, outdir)
    print('Done')


if __name__ == '__main__':
    main()
