import os
import cv2
import numpy as np


class SimpleOCR:

    def __init__(self):
        self.templates = list()
        for i in range(1, 10):
            im = cv2.imread(os.path.join('numbers', str(i) + '.png'))
            im_bin = self.im2bin(im)
            self.templates.append((i, im_bin))

    @classmethod
    def im2bin(cls, im):
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 240, 1, cv2.THRESH_BINARY)
        return binary

    @classmethod
    def cut(cls, im):
        assert im.shape == (18, 44), "not compatible"
        lst = list()
        lst.append(im[4: 14, 2: 10])
        lst.append(im[4: 14, 12: 20])
        lst.append(im[4: 14, 22: 30])
        lst.append(im[4: 14, 32: 40])
        return lst

    def determine(self, im: np.ndarray):
        consistency = list()
        for i, template in self.templates:
            consistency.append((i, (im == template).sum()))
        return max(consistency, key=lambda x: x[1])[0]

    def determine_all(self, im: np.ndarray):
        result = ''
        for i in self.cut(self.im2bin(im)):
            n = self.determine(i)
            result += str(n)
        return result

    def number_from_bytes(self, data: bytes):
        try:
            x = np.asarray(bytearray(data), dtype='uint8')
            im = cv2.imdecode(x, cv2.IMREAD_COLOR)
            return self.determine_all(im)
        except:
            return None


if __name__ == '__main__':
    path = 'tmp/codes/0.png'
    with open(path, 'rb') as f:
        print(SimpleOCR().number_from_bytes(f.read()))
