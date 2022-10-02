#!/usr/bin/python


import sys
import os
import fnmatch
from datetime import datetime, timedelta
from astral.geocoder import database, lookup
from astral.sun import sun
import pytz
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)


def parseTime(filename):
    t = os.path.basename(filename)
    t = t.replace("lapse_", "")
    t = t.replace(".jpg", "")
    t = datetime.strptime(t, '%b-%d-%Y_%H%M')
    return t


def isDay(filename, city, hourBuffer):
    t = parseTime(filename)
    timezone = pytz.timezone(city.timezone)
    t = timezone.localize(t)
    s = sun(city.observer, date=t)

    buf = timedelta(hours=float(hourBuffer))

    return s['sunrise']+buf < t < s['sunset']-buf

if __name__ == '__main__':
    dir = sys.argv[1]
    ext = sys.argv[2]
    city = lookup(sys.argv[3], database())
    hourBuffer = sys.argv[4]
    selectedFiles = []
    for root, dirs, files in os.walk(dir):
        for filename in fnmatch.filter(files, ext):
            filename = os.path.join(root, filename)
            if os.path.isfile(filename):
                if isDay(filename, city, hourBuffer):
                    selectedFiles.append(filename)
    selectedFiles.sort(key=parseTime)
    for filename in selectedFiles:
        print("file " + filename)






