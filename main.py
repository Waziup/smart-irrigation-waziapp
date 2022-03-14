#!/usr/bin/python
import usock
import os
from urllib.parse import urlparse
import pathlib
import requests
import json
import re

#---------------------#

usock.sockAddr = "/root/app/proxy.sock"


# Path to the root of the code
PATH = os.path.dirname(os.path.abspath(__file__))

#---------------------#
# Global Variables to receive sensor data
data = None

soil_moisture = None
humidity = None
temperature = None

moisturePercentage = None
out = None
#---------------------#

def index(url, body=""):
    
    return 200, b"Salam Goloooo", []

usock.routerGET("/", index)

#------------------#

def ui(url, body=''):
    filename = urlparse(url).path.replace("/ui/", "")
    if (len(filename) == 0):
        filename = 'index.html'

    #---------------#

    ext = pathlib.Path(filename).suffix

    extMap = {
        '': 'application/octet-stream',
        '.manifest': 'text/cache-manifest',
        '.html': 'text/html',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.svg':	'image/svg+xml',
        '.css':	'text/css',
        '.js': 'application/x-javascript',
        '.wasm': 'application/wasm',
        '.json': 'application/json',
        '.xml': 'application/xml',
    }

    if ext not in extMap:
        ext = ""

    conType = extMap[ext]

    #---------------#

    try:
        with open(PATH + '/ui/' + filename, mode='rb') as file:
            return 200, file.read(), [conType]
    except Exception as e:
        print("Error: ", e)
        return 404, b"File not found", []


usock.routerGET("/ui/(.*)", ui)
usock.routerPOST("/ui/(.*)", ui)

#------------------#

def sensorsGET(url, body=""): # function to GET sensors data from a device id
    print("begin of get sensors")
    # Replace with the device id
    deviceID = "dca632609cc6" 

    # url = "http://wazigate.local/devices/%s",%deviceID # local url
    # To fix GET local JSON. Returns HTTP Connection Pool error


    url = "http://waziup.wazigate-edge/devices/%s"%deviceID
    headers = {
        'accept': 'application/json',
        }
    response = requests.get(url, headers=headers)

    data = response.json()
    # print(data) # uncomment to see the JSON data

    # here, we get the sensors values using their position in the JSON
    for element in data["sensors"]:
        if re.findall("^humiditySensor_*",element['id'])  and re.findall("(?<=_).*",element["id"]) == ['1']:
            print("found humiditySensor: " + element["id"] + " value: " + str(element["value"]))
            humidity = element["value"]
        elif re.findall("^temperatureSensor_*",element['id'])  and re.findall("(?<=_).*",element["id"]) == ['2']:
            print("found temperatureSensor: " + element["id"] + " value: " + str(element["value"]))
            temperature = element["value"]
        elif re.findall("^analogOutput_*",element['id'])  and re.findall("(?<=_).*",element["id"]) == ['3']:
            print("found soilmoistureSensor: " + element["id"] + " value: " + str(element["value"]))
            soil_moisture = element["value"]

    # we now analyze the sensor data to get relevant insights for the user
    # moisturePercentage = ( 100.00 - ( (soil_moisture / 1023.00) * 100.00 ) )
    # moisturePercentage = round(moisturePercentage, 1) # round off % to 1 d.p

    moisturePercentage = soil_moisture 
    out = b"Soil moisture level = "
    out += str.encode(str(moisturePercentage))
    out += b"%"
    out += b"<br>Humidity = " # we put a line break, <br>, for the html display
    out += str.encode(str(humidity))
    out += b"<br>Temperature = "
    out += str.encode(str(temperature))

    out += b"<br>"
    out += b"_______________________________________________"
    out += b"<br>"

    # here, you can define your insights from the data:
    if( moisturePercentage <30):
        out += b"<br><b>Watering required. Moisture content low!</b>"

    elif( (moisturePercentage >60) and (humidity >60)):
        out += b"<br><b>Good plant environment.</b>"

    elif( (moisturePercentage <40) and (humidity <50)):
        out += b"<br><b>Watering required very soon.</b>"

    else:
        out += b"<br><b>Normal plant environment.</b>"
    
    return 200, out, []



usock.routerGET("/sensors", sensorsGET)

#------------------#

#------------------# 
if __name__ == "__main__":
    usock.start()
