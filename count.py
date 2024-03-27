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


# download coco.names if it doesn't exist
def prepare_coco():
    if not os.path.isfile('coco.names'):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names",
                                   "coco.names")


# download the weights and cfg files for YOLOv3

# load the coco.names file
def load_coco():
    prepare_coco()
    # load the classes
    classes = []
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    return classes


def prepare_yolo():
    if not os.path.isfile('yolov3.weights'):
        urllib.request.urlretrieve("https://pjreddie.com/media/files/yolov3.weights", "yolov3.weights")
    else:
        print("yolov3.weights already exists")
    if not os.path.isfile('yolov3.cfg'):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg",
                                   "yolov3.cfg")
    else:
        print("yolov3.cfg already exists")


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


def detect_objects(image, net):
    # get the output layer names
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
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

    # class ids detected
    class_ids = []
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
            if confidence > 0.05:
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
                class_ids.append(class_id)
                confidences.append(float(confidence))
    # apply non-max suppression
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    # create a list to store the bounding boxes after non-max suppression
    boxes_nms = []
    # loop through the indexes
    for i in indexes:
        box_to_append = boxes[i]
        box_to_append.append(class_ids[i])
        # get the bounding box
        boxes_nms.append(box_to_append)
    # return the list of bounding boxes
    return boxes_nms


# this function takes an image and a list of bounding boxes and draws the bounding boxes on the image
# it then returns the image with the bounding boxes drawn on it
def draw_boxes(image, boxes):
    # load the classes
    classes = load_coco()
    # get the height and width of the image
    height, width, channels = image.shape
    # loop through the bounding boxes
    for box in boxes:
        # get the top left corner
        class_id = box[4]
        x = box[0]
        y = box[1]
        # get the width and height
        w = box[2]
        h = box[3]
        # draw the bounding box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
        # put the label text above the bounding box
        cv2.putText(image, classes[class_id], (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    # return the image with the bounding boxes drawn on it
    return image


# parses the time from the filename
# uses the parseTime function from parseTimes.py
def get_sanitized_time(filename):
    return parseTime(filename).strftime("%m_%d_%Y_%H_%M_%S")


# parses the day from the filename
# uses the parseTime function from parseTimes.py
def get_day(filename):
    return parseTime(filename).strftime("%m_%d_%Y")


if __name__ == '__main__':
    # load the pre-trained model
    net = get_yolo()
    for img_file in sys.stdin:
        print("file " + img_file)
        img_file = img_file.rstrip()
        img = cv2.imread(img_file)
        boxes = detect_objects(img, net)
        if len(boxes) > 0:
            print(boxes)
            img = draw_boxes(img, boxes)
            # display the image
            cv2.imshow("image", img)
            # wait for 2 seconds
            cv2.waitKey(2000)
        else:
            print("no objects detected")
