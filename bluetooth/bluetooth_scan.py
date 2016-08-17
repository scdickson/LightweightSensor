from bluetooth import *
import bluetooth._bluetooth as bluez
import os
import pycurl
import time
import sqlite3

def lookup_oui(mac):
	manufacturer = 'Unknown'
	mac = mac.replace(':', '')
	mac = mac[0:6]
	f = open('/home/pi/defcon/oui.csv')
	for line in f:
		params = line.split(",")
		if(params[0] == 'MA-L' and len(params) > 1):
			if(mac == params[1]):
				manufacturer = params[2].replace('"', '')
				manufacturer = manufacturer.replace("'", "")
				break
	return manufacturer

c = pycurl.Curl()
c.setopt(c.CONNECTTIMEOUT, 5)
c.setopt(c.TIMEOUT, 10)
c.setopt(c.FAILONERROR, True)

f = open('/home/pi/defcon/sensor_properties', 'r')
sensor_name = f.readline()
sensor_name = sensor_name[0:len(sensor_name)-1]
bdb = sqlite3.connect('/home/pi/defcon/bluetooth/bluetooth.db')
sldb = sqlite3.connect('/home/pi/defcon/sensor_log.db')
bc = bdb.cursor()
slc = sldb.cursor()

try:
	c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/sensor_log.json')
	c.setopt(c.POSTFIELDS, "{\"event\": \"Start Bluetooth Scan\", \"sensor\": \"" + sensor_name + "\", \"event_time\": \"" + time.strftime("%m/%d/%y %H:%M:%S") + "\"}" )
	c.perform()
	slc.execute("INSERT INTO events VALUES (NULL, 1, 'Start Bluetooth Scan', '" + sensor_name + "', '" + time.strftime("%m/%d/%y %H:%M:%S") + "')")
	sldb.commit()
except pycurl.error, error:
	slc.execute("INSERT INTO events VALUES (NULL, 0, 'Start Bluetooth Scan', '" + sensor_name + "', '" + time.strftime("%m/%d/%y %H:%M:%S") + "')")
	sldb.commit()

c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/bt_devices.json')

while True:
	nearby_devices = discover_devices(lookup_names = True)
	for name, addr in nearby_devices:
		try:
			manufacturer = lookup_oui(name)

			c.setopt(c.POSTFIELDS, "{\"MAC\": \"" + name + "\", \"name\": \"" + addr + "\", \"manufacturer\": \"" + manufacturer + "\", \"time_detected\": \"" + time.strftime("%m/%d/%y %H:%M:%S") + "\", \"sensor_name\": \"" + sensor_name + "\"}")
			c.perform()
			bc.execute("INSERT INTO scan_result VALUES (NULL, 1, 0, '" + name + "', '" + addr + "', '" + manufacturer + "', '', '', '" + time.strftime("%m/%d/%y %H:%M:%S") + "', '" + sensor_name + "')")
			bdb.commit()

		except pycurl.error, error:
			bc.execute("INSERT INTO scan_result VALUES (NULL, 0, 0, '" + name + "', '" + addr + "', '" + manufacturer + "', '', '', '" + time.strftime("%m/%d/%y %H:%M:%S") + "', '" + sensor_name + "')")
			bdb.commit()
	os.system("sudo python /home/pi/defcon/bluetooth/ble_scanner.py")
	time.sleep(60*15)
