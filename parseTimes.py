#!/usr/bin/python


import sys
import os
import time
import fnmatch
from datetime import datetime
from astral import Astral

def isMidday(filename):
    t=os.path.basename(filename)
    t=t.replace("lapse_", "")
    t=t.replace(".jpg", "")
    t=datetime.strptime(t, '%b-%d-%Y_%H%M')
    print(t)
    return False

if __name__ == '__main__':


    dir=sys.argv[1]
    ext=sys.argv[2]

    for root, dirs, files in os.walk(dir):
        print(root)
        for filename in fnmatch.filter(files, ext):
            filename = os.path.join(root, filename)
            if os.path.isfile(filename):            
                print(isMidday(filename))




