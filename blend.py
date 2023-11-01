import sys
import fileinput
import numpy as np
import cv2
import glob
from parseTimes import *
# https://stackoverflow.com/questions/57723968/blending-multiple-images-with-opencv


def blend(list_images): # Blend images equally.

    equal_fraction = 1.0 / (len(list_images))

    output = np.zeros_like(list_images[0])

    for img in list_images:
        output = output + img * equal_fraction
        # output = cv2.addWeighted(output, 1, img, equal_fraction, 0)

    output = output.astype(np.uint8)
    return output


def read_image_list(file_list_images):
    image_list = []
    for filename in file_list_images:
        im = cv2.imread(filename)
        image_list.append(im)
    return image_list


def blend_image_list(file_blend):
    images = read_image_list(file_blend)
    blended = blend(images)
    return blended


def get_sanitized_time(filename):
    print(filename)
    return parseTime(filename).strftime("%m_%d_%Y_%H_%M_%S")


if __name__ == '__main__':
    dir_out_img = sys.argv[1]
    blendEvery = int(sys.argv[2])
    files_to_blend = []
    for img in sys.stdin:
        files_to_blend.append(img.rstrip())

        if len(files_to_blend) >= blendEvery:
            f1 = get_sanitized_time(files_to_blend[0])
            print(f1)
            f2 = get_sanitized_time(files_to_blend.pop())
            print(f2)
            cv2.imwrite(dir_out_img + "test.jpg", blend_image_list(files_to_blend), [cv2.IMWRITE_JPEG_QUALITY, 95])
            files_to_blend = []
