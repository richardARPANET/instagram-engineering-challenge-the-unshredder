import os
import math
import operator
from functools import reduce

from PIL import Image, ImageChops

SHRED_WIDTH = 32
IMG_WIDTH, IMG_HEIGHT, NUM_COLS = None, None, None


def openimg(path, size=None):
    img = Image.open(path)
    return img.resize(size=(size or img.size)).convert('RGBA')


def get_cols(img):
    img_height = img.size[1]
    for shred_number in range(NUM_COLS):
        x1, y1 = SHRED_WIDTH * (shred_number), 0
        x2, y2 = x1 + SHRED_WIDTH, img_height
        source_region = img.crop(box=(x1, y1, x2, y2))
        yield source_region


def reorder(shredded_cols, original_cols):

    def root_mean_square_difference(im1, im2):
        hist = ImageChops.difference(im1, im2).histogram()
        return math.sqrt(
            reduce(
                operator.add,
                map(lambda hist, i: hist * (i ** 2), hist, range(256))
            ) / (float(im1.size[0]) * im1.size[1])
        )

    for region in original_cols:
        img_diffs = [
            root_mean_square_difference(region, img) for img in shredded_cols
        ]
        idx_of_least_error = img_diffs.index(min(img_diffs))
        yield shredded_cols[idx_of_least_error]


def unshred():
    global IMG_WIDTH
    global IMG_HEIGHT
    global NUM_COLS

    shredded = openimg('images/shredded.png')
    IMG_WIDTH, IMG_HEIGHT = shredded.size
    NUM_COLS = int(IMG_WIDTH / SHRED_WIDTH)
    unshredded = Image.new('RGBA', (IMG_WIDTH, IMG_HEIGHT))

    orig_img = openimg('images/original.png', size=shredded.size)
    shredded_img_cols = tuple(get_cols(shredded))
    orig_img_cols = tuple(get_cols(orig_img))

    for idx, column_img in enumerate(
        reorder(shredded_img_cols, orig_img_cols)
    ):
        unshredded.paste(im=column_img, box=(idx * SHRED_WIDTH, 0))

    unshredded.save('unshredded.png', 'PNG')
    os.system('open unshredded.png')


if __name__ == '__main__':
    unshred()
