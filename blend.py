import cv2
import numpy as np
import matplotlib.image as mpimg


# https://stackoverflow.com/questions/57723968/blending-multiple-images-with-opencv
def blend(list_images): # Blend images equally.

    equal_fraction = 1.0 / (len(list_images))

    output = np.zeros_like(list_images[0])

    for img in list_images:
        output = output + img * equal_fraction

    output = output.astype(np.uint8)
    return output


if __name__ == '__main__':
    past_frame = None
    print("Blending lapse")
