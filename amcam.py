#!/usr/bin/python

# https://gist.github.com/FutureSharks/ab4c22b719cdd894e3b7ffe1f5b8fd91
# https://www.geeksforgeeks.org/detect-cat-faces-in-real-time-using-python-opencv/

import cv2
import io
import numpy as np
import re
import os
from pyvesync_v2 import VeSync
import time
from amcrest import AmcrestCamera


def getCamera():
    camera = AmcrestCamera(os.getenv("AMCREST_IP"), os.getenv("AMCREST_PORT"), os.getenv("AMCREST_USR"), os.getenv('AMCREST_PWD')).camera
    return camera


camera = getCamera()

sleep_minutes = 1

# camera.rotation = 180
# Motion detection sensitivity
min_area = 100
sleep_minutes = .1
imageDir = os.getenv("AMCREST_OUT")

manager = VeSync(os.getenv('VE_SYNC_EMAIL'), os.getenv('VE_SYNC_PWD'), time_zone="America/Chicago")

manager.login()
# Get/Update Devices from server - populate device lists
manager.update()

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalcatface_extended.xml')


def handle_new_frame(frame, past_frame, min_area):
    # if the first frame is None, initialize it because there is no frame for comparing the current one with a previous one
    if past_frame is None:
        past_frame = frame
        return past_frame

    # check if past_frame and current have the same sizes
    (h_past_frame, w_past_frame) = past_frame.shape[:2]
    (h_current_frame, w_current_frame) = frame.shape[:2]
    if h_past_frame != h_current_frame or w_past_frame != w_current_frame:
        print('Past frame and current frame do not have the same sizes {0} {1} {2} {3}'.format(h_past_frame, w_past_frame, h_current_frame, w_current_frame))
        return

    # compute the absolute difference between the current frame and first frame
    frame_detla = cv2.absdiff(past_frame, frame)
    # then apply a threshold to remove camera motion and other false positives (like light changes)
    thresh = cv2.threshold(frame_detla, 50, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0]

    # loop over the contours
    found = False
    for c in cnts:
        # if the contour is too small, ignore it
        if found or cv2.contourArea(c) < min_area:
            continue
        print("Motion detected!")
        found = True
    if found:
        saveCntFrame(frame, c)
        capture("pre")
        # turnOn()
        detectCats(getFullFrame())
        capture("post")
        getContourCenter(frame, c)

        time.sleep(60*sleep_minutes/2)
        
        print("off")
        # turnOff()
        print("establish")
        return getMotionFrame()


def getContourCenter(frame, cnts):
    M = cv2.moments(cnts)
    # if M['m00'] != 0:
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    #     cv.drawContours(image, [i], -1, (0, 255, 0), 2)
    cv2.circle(frame, (cx, cy), 7, (0, 0, 255), -1)
    cv2.putText(frame, "center", (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    # print(f"x: {cx} y: {cy}")
    saveFrame(frame, 'motion-rec-contour')


def getCurrentAbsPos():
    statusString = camera.ptz_status()
    statusArray = statusString.splitlines()
    print(statusString)
    print(statusArray)
    print(statusArray[3].replace(".*=", ""))

    posX = re.sub(".*=", "", statusArray[3])
    posY = re.sub(".*=", "", statusArray[4])
    posZ = re.sub(".*=", "", statusArray[5])
    xyz=[posX, posY, posZ]

    return xyz


def getAngleFromCurrentToCountour():
    return None


def centerCameraOnCurrent():
    return None


def getFullFrame():
    data = np.frombuffer(io.BytesIO(camera.snapshot().data).getvalue(), dtype=np.uint8)
    frame = cv2.imdecode(data, 1)
    time.sleep(2)

    return frame


def getGray():
    gray = cv2.cvtColor(getFullFrame(), cv2.COLOR_BGR2GRAY) # We apply a black & white filter
    return gray


def getMotionFrame():
    frame = getGray()
    (h, w) = frame.shape[:2]
    r = 500 / float(w)
    dim = (500, int(h * r))
    frame = cv2.resize(frame, dim, cv2.INTER_AREA) # We resize the frame
    gray = cv2.GaussianBlur(frame, (21, 21), 0) # Then we blur the picture
    return gray


def detectCats(frame):
    grayCat = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(grayCat, 1.05, 3)

    found = False
    for (x, y,w, h) in faces:
        # To draw a rectangle in a face  
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
        roi_gray = grayCat[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        found = True
    if found:
        print("found a cat!!")
        saveFrame(frame, 'motion-cat')
    else:
        print("no cat")


def saveFrame(frame, tag):
    t = time.localtime()
    outDir = getOutDir(t)
    f = outDir+tag+getTimeStamp(t)+'.jpg'
    print(f)
    cv2.imwrite(f, frame)


def saveCntFrame(frame, cnt):
    frame = cv2.drawContours(frame, [cnt], 0, (0,255,0), 3)
    saveFrame(frame, 'motion-rec-')


def getTimeStamp(t):
    return time.strftime('%b-%d-%Y_%H%M', t)


def getOutDir(t):
    subDir = time.strftime('%b-%d-%Y', t)
    outDir = os.path.join(imageDir, subDir+"/")
    os.makedirs(outDir, exist_ok=True)
    return outDir


def capture(tag):
    saveFrame(getFullFrame(), tag)


def turnOn():
    for device in manager.outlets:
            print(device.device_name)
            if device.device_name == "Couch living room":
                device.turn_off()
                device.turn_on()


def turnOff():
    for device in manager.outlets:
        if device.device_name == "Couch living room":
            # device.turn_on()
            device.turn_off()
if __name__ == '__main__':
    past_frame = None
    print("Starting motion detection")

    try:
        while True:
            print("detecting")
            # A new snapshot
            frame = getMotionFrame()
            getCurrentAbsPos()
            if frame is not None:
                # if no motion and past frame is not None, return val will be None. Else return will be frame
                # If motion, return will be new sshot
                past_frame = handle_new_frame(frame, past_frame, min_area)
            else:
                print("No more frame")
    finally:
        print("Exiting")