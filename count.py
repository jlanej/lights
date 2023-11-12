from signal import signal, SIGPIPE, SIG_DFL
import cv2
import sys
import numpy as np
import urllib.request
import os

from parseTimes import parseTime

# https://stackoverflow.com/questions/57723968/blending-multiple-images-with-opencv
# wget https://pjreddie.com/media/files/yolov3.weights
# https://pjreddie.com/darknet/yolo/

signal(SIGPIPE, SIG_DFL)


# download the weights and cfg files for YOLOv3

def prepare_yolo():
    if not os.path.isfile('yolov3.weights'):
        urllib.request.urlretrieve("https://pjreddie.com/media/files/yolov3.weights", "yolov3.weights")
    if not os.path.isfile('yolov3.cfg'):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg", "yolov3.cfg")


# Loads the YOLOv3 model and returns a network object
def get_yolo():
    prepare_yolo()
    # load the pre-trained model
    net = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
    return net


# this function takes an image and detects objects in the image using opencv
# it then returns a list of bounding boxes for these objects
# the bounding boxes are in the format [x,y,w,h]
# where x and y are the coordinates of the top left corner of the bounding box
# and w and h are the width and height of the bounding box
# the function takes an image as input and returns a list of bounding boxes


def detect_objects(image,network="yolov3"):
    # load the pre-trained model
    net = get_yolo()
    # load the classes
    classes = []
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    # get the output layer names
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    # get the height and width of the image
    height, width, channels = image.shape
    # create a blob from the image
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0),
                                 True, crop=False)
    # pass the blob through the network and get the output
    net.setInput(blob)
    outs = net.forward(output_layers)
    # create a list to store the bounding boxes
    boxes = []
    # create a list to store the confidences
    confidences = []
    # loop through the output
    for out in outs:
        # loop through the detections
        for detection in out:
            # get the confidence
            scores = detection[5:]
            # get the class id
            class_id = np.argmax(scores)
            # get the confidence
            confidence = scores[class_id]
            # check if the confidence is greater than 0.5
            if confidence > 0.5:
                # get the center coordinates
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                # get the width and height
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # get the top left corner
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                # append the bounding box and confidence to their lists
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
    # apply non-max suppression
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    # create a list to store the bounding boxes after non-max suppression
    boxes_nms = []
    # loop through the indexes
    for i in indexes:
        # get the bounding box
        boxes_nms.append(boxes[i[0]])
    # return the list of bounding boxes
    return boxes_nms

# parses the time from the filename
# uses the parseTime function from parseTimes.py
def get_sanitized_time(filename):
    return parseTime(filename).strftime("%m_%d_%Y_%H_%M_%S")


# parses the day from the filename
# uses the parseTime function from parseTimes.py
def get_day(filename):
    return parseTime(filename).strftime("%m_%d_%Y")


if __name__ == '__main__':
    for img in sys.stdin:
        img = img.rstrip()
        detect_objects(cv2.imread(img))
        print(get_day(img))
