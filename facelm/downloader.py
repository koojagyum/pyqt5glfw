import bz2
import os
import sys
import tarfile
import urllib.request

from os.path import abspath
from os.path import isfile
from os.path import join
from tqdm import tqdm


MODEL_URL = 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'
MODEL_DIRPATH = './model'
MODEL_PATH = './model/shape_predictor_68_face_landmarks.dat'
BZ2_PATH = './model/shape_predictor_68_face_landmarks.dat.bz2'


def print_overline(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()


def build_format(current_byte, total_byte):
    current_kb = int(current_byte / 1024)
    total_kb = int(total_byte / 1024)
    string = '{:d} / {:d} Kbyte  {:6.2f} %'.format(
        current_kb,
        total_kb,
        current_byte * 100. / total_byte
    )

    return string


def extract_bz2(bz2path, todir='.'):
    todir = abspath(todir)
    newpath = join(todir, bz2path[:-4])
    zipfile = bz2.BZ2File(bz2path)
    data = zipfile.read()
    with open(newpath, 'wb') as f:
        f.write(data)
        return newpath


def download(url, dirpath='.'):
    dirpath = abspath(dirpath)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    filepath = join(dirpath, url.split('/')[-1])
    print('Downloading {}'.format(filepath))
    u = urllib.request.urlopen(url)
    with open(filepath, 'wb') as f:
        meta = u.info()
        file_size = int(meta['Content-Length'])
        print('file_size: {:d} Kbyte'.format(int(file_size / 1024)))

        file_size_dl = 0
        block_sz = 8192

        t = tqdm(
            total=file_size//1024,
            unit='Byte',
            unit_scale=True,
        )
        while True:
            buf = u.read(block_sz)
            if not buf:
                break

            f.write(buf)
            t.update(n=len(buf))

        t. close()
        print('\nDone')
        return filepath


def check_model():
    modelpath = MODEL_PATH
    if isfile(modelpath):
        return modelpath

    bz2path = BZ2_PATH
    if not isfile(bz2path):
        bz2path = download(MODEL_URL, MODEL_DIRPATH)

    print('Extracting', bz2path)
    modelpath = extract_bz2(bz2path, MODEL_DIRPATH)
    return modelpath


def test_extract():
    filepath = abspath(BZ2_PATH)
    if not isfile(filepath):
        filepath = download(MODEL_URL, './model')
    print('Extracting', filepath)
    extract_bz2(filepath, './model')


def test_download():
    filepath = download(MODEL_URL, './model')


def main():
    modelpath = check_model()
    print('modelpath:', modelpath)


if __name__ == '__main__':
    main()
