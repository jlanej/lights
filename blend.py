import sys
import numpy as np
import cv2
import glob


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


if __name__ == '__main__':
    dir_img = sys.argv[1]
    dir_out_img = sys.argv[2]

    # print("blending" +len(glob.glob(dir_img+'/*.jpg')))
    images = read_image_list(glob.glob(dir_img+'/*.jpg'))
    blended = blend(images)
    cv2.imwrite(dir_out_img+"test.jpg", blended, [cv2.IMWRITE_JPEG_QUALITY, 95])


