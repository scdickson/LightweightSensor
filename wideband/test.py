import sys
import os
import pycurl
import sqlite3
import time

lower_freq = '25M'
upper_freq = '1700M'
gain = '25'
bin_size = '1M'

f = open('/home/pi/defcon/sensor_properties', 'r')
sensor_name = f.readline()
sensor_name = sensor_name[0:len(sensor_name)-1]

c = pycurl.Curl()
c.setopt(c.CONNECTTIMEOUT, 5)
c.setopt(c.TIMEOUT, 10)
c.setopt(c.FAILONERROR, True)
c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/wb_scan.json')
image_id = 'null'

c.setopt(c.POSTFIELDS, "{\"wbscan_image_url\": \"http://i.imgur.com/" + str(image_id) + ".png\", \"lower_freq\": \"" + lower_freq + "\", \"upper_freq\": \"" + upper_freq + "\", \"gain\": \"" + gain + "\", \"bin_size\": \"" + bin_size + "\", \"time_of_scan\": \"" + time.strftime("%m/%d/%y %H:%M:%S") + "\", \"sensor\": \"" + sensor_name + "\"}")
c.perform()
