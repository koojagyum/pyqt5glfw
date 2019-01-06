import argparse
import cv2
import math
import numpy as np
import os

from util.geo import to_scr


def headposeof(lm, img):
    # 3D model points
    ref_indices = [33, 8, 36, 45, 48, 54]
    image_pts = lm[ref_indices].astype(np.float32)
    model_pts = np.array([
        (0.0, 0.0, 0.0),             # Nose tip
        (0.0, -330.0, -65.0),        # Chin
        (-225.0, 170.0, -135.0),     # Left eye left corner
        (225.0, 170.0, -135.0),      # Right eye right corne
        (-150.0, -150.0, -125.0),    # Left Mouth corner
        (150.0, -150.0, -125.0)      # Right mouth corner                     
    ], dtype=np.float32)

    # Camera internals
    size = img.shape
    focal_length = size[1]
    center = (size[1]/2, size[0]/2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype=np.float32)

    dist_coeffs = np.zeros((4,1))  # Assuming no lens distortion
    success, rvec, tvec = cv2.solvePnP(
        model_pts,
        image_pts,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    # Rotation matrix
    rmat, jacobian = cv2.Rodrigues(rvec)

    # Euler angle
    return mat2euler(rmat)


# this conversion uses conventions as described on page:
# https://www.euclideanspace.com/maths/geometry/rotations/euler/index.htm
# Coordinate System: right hand
# Positive angle: right hand
# Order of euler angles: heading first, then attitude, then bank
# matrix row column ordering:
# [m00 m01 m02]
# [m10 m11 m12]
# [m20 m21 m22]
def mat2euler(m):
    # Assuming the angles are in radians
    if m[0,1] > 0.998:  # singularity at north pole
        heading = math.atan2(m[0,2], m[2,2])
        attitude = math.pi / 2.0
        bank = 0.0
        return heading, attitude, bank
    if m[1,0] < -0.998:  # singularity at south pole
        heading = math.atan2(m[0,2], m[2,2])
        attitude = -math.pi / 2.0
        bank = 0.0
        return heading, attitude, bank

    heading = math.atan2(-m[2,0], m[0,0])
    attitude = math.atan2(-m[1,2], m[1,1])
    bank = math.asin(m[1,0])
    return heading, attitude, bank


def test_headpose(imgfile):
    from .detector import FaceDetector
    from .detector import plot_lmindices

    detector = FaceDetector()
    img = cv2.imread(imgfile)
    _, shapes = detector.detect(img)

    yaw, pitch, roll = headposeof(shapes[0], img)
    yaw, pitch, roll = math.degrees(yaw), \
                       math.degrees(pitch), \
                       math.degrees(roll)

    text = '{}, {}, {}'.format(int(yaw), int(pitch), int(roll))
    print('headpose: {}'.format(text))

    plot_lmindices(img, shapes[0])


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
        help='Path for input image file'
    )

    args = parser.parse_args()
    verbose = args.verbose
    input_path = args.input
    input_path = os.path.expanduser(input_path)

    test_headpose(input_path)


if __name__ == '__main__':
    main()
