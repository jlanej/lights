#!/usr/bin/python


import sys
import os
import time
import fnmatch
from datetime import datetime, timezone
import astral
from astral.geocoder import database, lookup
from astral.sun import sun
import pytz

def isDay(filename,city):
    t=os.path.basename(filename)
    t=t.replace("lapse_", "")
    t=t.replace(".jpg", "")
    t=datetime.strptime(t, '%b-%d-%Y_%H%M')
    # t.replace(tzinfo=timezone.CDT)
    timezone = pytz.timezone(city.timezone)
    t = timezone.localize(t)
    s = sun(city.observer, date=t)
    return s['sunrise'] < t < s['sunset']

if __name__ == '__main__':


    dir=sys.argv[1]
    ext=sys.argv[2]
    city=lookup(sys.argv[3], database())

#     print((
#     f"Information for {city.name}/{city.region}\n"
#     f"Timezone: {city.timezone}\n"
#     f"Latitude: {city.latitude:.02f}; Longitude: {city.longitude:.02f}\n"
# ))

    for root, dirs, files in os.walk(dir):
        for filename in fnmatch.filter(files, ext):
            filename = os.path.join(root, filename)
            if os.path.isfile(filename):            
                if isDay(filename,city):
                    print(filename)




