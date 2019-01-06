import cv2
import numpy as np


def scale(w, h, x, y, maximum=True):
    nw = y * w / h
    nh = x * h / w
    if maximum ^ (nw >= x):
        return nw or 1, y
    return x, nh or 1


def to_scr(vert, img, inverty=True):
    return to_scr_res(vert, (img.shape[1], img.shape[0]), inverty=inverty)


def to_scr_res(vert, res=(1.0, 1.0), inverty=True):
    vert_scr = vert.copy()

    vert_scr[:,1] = vert_scr[:,1] * (1.0, -1.0)[inverty]
    vert_scr = (vert_scr + 1.0) * 0.5
    vert_scr = vert_scr * np.array([res[0], res[1]], dtype=np.float32)

    return vert_scr


def to_ndc(vert, res=(1.0, 1.0), inverty=True):
    vert_ndc = vert.copy()

    modifier = (1.0, -1.0)[inverty]
    vert_ndc[:,0] = vert_ndc[:,0] * 2.0 / res[0] - 1.0
    vert_ndc[:,1] = (vert_ndc[:,1] * 2.0 / res[1] - 1.0) * modifier

    return vert_ndc


def intersect_lines(p1, p2, p3, p4):
    a1 = p2[1] - p1[1];
    b1 = p1[0] - p2[0];
    c1 = a1 * p1[0] + b1 * p1[1];

    a2 = p4[1] - p3[1];
    b2 = p3[0] - p4[0];
    c2 = a2 * p3[0] + b2 * p3[1];

    determinant = a1 * b2 - a2 * b1;
    if determinant == 0.0:
        # The lines are parallel.
        return np.array([0.0, 0.0], dtype=np.float32)

    x = (b2 * c1 - b1 * c2) / determinant;
    y = (a1 * c2 - a2 * c1) / determinant;

    return np.array([x, y], dtype=np.float32)


def centroid(pts, aspect_ratio=1.0):
    apply_ratio = np.array([1.0, aspect_ratio], dtype=np.float32)
    restore_ratio = np.array([1.0, 1.0/aspect_ratio], dtype=np.float32)

    p = pts * apply_ratio
    n = pts.shape[0] - 1
    signed_area = 0.0
    a = 0.0
    current = [0.0, 0.0]

    for i in range(0, n):
        a = p[i,0] * p[i+1,1] - p[i+1,0] * p[i,1]
        signed_area += a
        current[0] += (p[i,0] + p[i+1,0]) * a
        current[1] += (p[i,1] + p[i+1,1]) * a

    a = p[n,0] * p[0,1] - p[0,0] * p[n,1]
    signed_area += a
    current[0] += (p[n,0] + p[0,0]) * a
    current[1] += (p[n,1] + p[0,1]) * a

    signed_area *= 0.5
    current[0] /= (6.0 * signed_area)
    current[1] /= (6.0 * signed_area)

    return np.array(current, dtype=np.float32) * restore_ratio
