import sqlite3
import pycurl
import os
import time

c = pycurl.Curl()
c.setopt(c.CONNECTTIMEOUT, 5)
c.setopt(c.TIMEOUT, 8)
c.setopt(c.FAILONERROR, True)

while True:
    	time.sleep(60*20)
    	#bluetooth
	db = sqlite3.connect('/home/pi/defcon/bluetooth/bluetooth.db')
	cur = db.cursor()
	for row in cur.execute('SELECT * FROM scan_result WHERE upload = 0'):
		if row[2] == 0: #Bluetooth
			c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/bt_devices.json')
			try:
				c.setopt(c.POSTFIELDS, "{\"MAC\": \"" + row[3] + "\", \"name\": \"" + row[4].encode('ascii', 'ignore') + "\", \"time_detected\": \"" + row[8] + "\", \"sensor_name\": \"" + row[9] + "\", \"manufacturer\": \"" + row[5] + "\"}")
				c.perform()
				cur.execute("UPDATE scan_result SET upload = 1 WHERE eid = " + str(row[0]))
				db.commit()
			except pycurl.error, error:
				errornum, errorstr = error
				print(errorstr)
		elif row[2] == 1: #BLE
			c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/ble_devices.json')
			try:
				c.setopt(c.POSTFIELDS, "{\"MAC\": \"" + row[3] + "\", \"name\": \"" + row[4].encode('ascii', 'ignore') + "\", \"time_detected\": \"" + row[8] + "\", \"sensor_name\": \"" + row[9] + "\", \"manufacturer\": \"" + row[5] + "\", \"RSSI\": \"" + row[6] + "\"}")
				c.perform()
				cur.execute("UPDATE scan_result SET upload = 1 WHERE eid = " + str(row[0]))
				db.commit()
			except pycurl.error, error:
				errornum, errorstr = error
				print(errorstr)

    	#wideband
	db = sqlite3.connect('/home/pi/defcon/wideband/wideband.db')
	cur = db.cursor()
	c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/wb_scan.json')
	for row in cur.execute('SELECT * FROM scan_result WHERE upload = 0'):
		try:
			c.setopt(c.POSTFIELDS, "{\"wbscan_image_url\": \"" + row[2] + "\", \"lower_freq\": \"" + row[5] + "\", \"upper_freq\": \"" + row[6] + "\", \"gain\": \"" + row[7] + "\", \"bin_size\": \"" + row[8] + "\", \"time_of_scan\": \"" + row[4] + "\", \"sensor\": \"" + row[3] + "\"}")
			c.perform()
			cur.execute("UPDATE scan_result SET upload = 1 WHERE eid = " + str(row[0]))
			db.commit()
		except pycurl.error, error:
			errornum, errorstr = error
			print(errorstr)

    	#logs
	db = sqlite3.connect('/home/pi/defcon/sensor_log.db')
	cur = db.cursor()
	c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/sensor_log.json')
	for row in cur.execute('SELECT * FROM events WHERE upload = 0'):
		try:
			c.setopt(c.POSTFIELDS, "{\"event\": \"" + row[2] + "\", \"sensor\": \"" + row[3] + "\", \"event_time\": \"" + row[4] + "\"}" )
			c.perform()
			cur.execute("UPDATE events SET upload = 1 WHERE eid = " + str(row[0]))
			db.commit()
		except pycurl.error, error:
			errornum, errorstr = error
			print(errorstr)
