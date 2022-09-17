#!/usr/bin/python

# https://gist.github.com/FutureSharks/ab4c22b719cdd894e3b7ffe1f5b8fd91
# https://www.geeksforgeeks.org/detect-cat-faces-in-real-time-using-python-opencv/

import cv2
import io
import numpy as np
import os
import time
from amcrest import AmcrestCamera


def getCamera():
    camera = AmcrestCamera(os.getenv("AMCREST_IP"), os.getenv("AMCREST_PORT"), os.getenv("AMCREST_USR"), os.getenv('AMCREST_PWD')).camera
    return camera


camera = getCamera()

sleep_minutes = 1
imageDir = os.getenv("AMCREST_OUT")


def getFullFrame():
    data = np.frombuffer(io.BytesIO(camera.snapshot().data).getvalue(), dtype=np.uint8)
    frame = cv2.imdecode(data, 1)
    return frame


def saveFrame(frame, tag):
    t = time.localtime()
    outDir = getOutDir(t)
    f = outDir+tag+getTimeStamp(t)+'.jpg'
    print(f)
    cv2.imwrite(f, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])


def getTimeStamp(t):
    return time.strftime('%b-%d-%Y_%H%M', t)


def getOutDir(t):
    subDir = time.strftime('%b-%d-%Y', t)
    outDir = os.path.join(imageDir, subDir+"/")
    os.makedirs(outDir, exist_ok=True)
    return outDir


def capture(tag):
    saveFrame(getFullFrame(), tag)

if __name__ == '__main__':
    past_frame = None
    print("Starting lapse")

    try:
        while True:
            print("snapping")
            capture("lapse_")
            time.sleep(60*sleep_minutes)

    finally:
        print("Exiting")

