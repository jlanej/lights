from signal import signal, SIGPIPE, SIG_DFL
# adding the parent directory to
# the sys.path.
import fileinput
import numpy as np
import cv2
import glob
import os
import sys
import parseTimes

# https://stackoverflow.com/questions/57723968/blending-multiple-images-with-opencv

signal(SIGPIPE, SIG_DFL)

# this function takes an image and detects objects in it
# it returns the image with the detected objects outlined
def detect_objects(img):


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
    return parseTime(filename).strftime("%m_%d_%Y_%H_%M_%S")


def get_day(filename):
    return parseTime(filename).strftime("%m_%d_%Y")


def get_sanitized_name(flist):
    return get_sanitized_time(flist[0])+"_to_"+get_sanitized_time(flist[len(flist)-1])


if __name__ == '__main__':
    dir_out_img = sys.argv[1]
    for img in sys.stdin:
        img = img.rstrip()
        print(get_day(img))
