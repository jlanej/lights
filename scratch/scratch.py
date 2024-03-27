
def prepare_yolo_tiny():
    if not os.path.isfile('yolov3-tiny.weights'):
        urllib.request.urlretrieve("https://pjreddie.com/media/files/yolov3-tiny.weights", "yolov3-tiny.weights")
    else:
        print("yolov3-tiny.weights already exists")
    if not os.path.isfile('yolov3-tiny.cfg'):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg",
                                   "yolov3-tiny.cfg")
    else:
        print("yolov3-tiny.cfg already exists")

def get_yolo_tiny():
    prepare_yolo_tiny()
    # load the pre-trained model
    net = cv2.dnn.readNetFromDarknet('yolov3-tiny.cfg', 'yolov3-tiny.weights')
    return net



# prepare darknet weights and cfg files
def prepare_darknet():
    if not os.path.isfile('darknet19.weights'):
        urllib.request.urlretrieve("https://pjreddie.com/media/files/darknet.weights", "darknet.weights")
    if not os.path.isfile('darknet.cfg'):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/darknet.cfg",
                                   "darknet.cfg")


# load darknet weights and cfg files
def load_darknet():
    prepare_darknet()
    # load the pre-trained model
    net = cv2.dnn.readNetFromDarknet('darknet.cfg', 'darknet.weights')
    return net

