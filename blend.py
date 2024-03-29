import sys
import fileinput
import numpy as np
import cv2
import glob
from parseTimes import *
import argparse
# https://stackoverflow.com/questions/57723968/blending-multiple-images-with-opencv
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

def read_image_list(file_list_images):
    image_list = []
    for filename in file_list_images:
        im = cv2.imread(filename)
        image_list.append(im)
    return image_list


def blend(list_images): # Blend images equally.

    equal_fraction = 1.0 / (len(list_images))

    output = np.zeros_like(list_images[0])

    for img in list_images:
        output = output + img * equal_fraction
        # output = cv2.addWeighted(output, 1, img, equal_fraction, 0)

    output = output.astype(np.uint8)
    return output

def blend_image_list(file_blend):
    images = read_image_list(file_blend)
    blended = blend(images)
    return blended


def get_sanitized_time(filename):
    return parseTime(filename).strftime("%m_%d_%Y_%H_%M_%S")

def get_year_month(filename):
    return parseTime(filename).strftime("%m_%Y")

def get_day(filename):
    return parseTime(filename).strftime("%m_%d_%Y")


def get_sanitized_name(flist):
    return get_sanitized_time(flist[0])+"_to_"+get_sanitized_time(flist[len(flist)-1])


def add_timestamp(img_file,stamp_file):
    img = cv2.imread(img_file)
    img = add_text(img, get_year_month(stamp_file))
    return img

def add_text(cvimg,text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner = (10, 250)
    fontScale = 10
    fontColor = (255, 255, 255)
    lineType = 2
    cv2.putText(cvimg, text, bottom_left_corner, font, fontScale, fontColor, lineType)
    return cvimg


if __name__ == '__main__':

    dir_out_img = sys.argv[1]
    blendEvery = int(sys.argv[2])
    timestamp = sys.argv[3]
    files_to_blend = []
    cur_day = ""
    next_day = ""
    for img in sys.stdin:
        img = img.rstrip()
        if blendEvery > 1:
            if cur_day == "":
                cur_day = get_day(img)

            if cur_day == get_day(img):
                files_to_blend.append(img)
            else:
                cur_day = ""
                files_to_blend = []

            if len(files_to_blend) >= blendEvery:
                output = dir_out_img + get_sanitized_name(files_to_blend)+".jpg"
                if not os.path.isfile(output):
                    cv2.imwrite(output, blend_image_list(files_to_blend), [cv2.IMWRITE_JPEG_QUALITY, 95])

                if timestamp:
                    current_output = output
                    output = dir_out_img + get_sanitized_name(files_to_blend)+"_timestamp.jpg"
                    if not os.path.isfile(output):
                        cv2.imwrite(output, add_timestamp(current_output,files_to_blend[0]), [cv2.IMWRITE_JPEG_QUALITY, 95])
                files_to_blend = []
                print("file " + output)

        else:
            print("file " + img)
