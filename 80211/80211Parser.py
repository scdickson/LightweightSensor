import os
import sys
import time
import pycurl
import sqlite3

def lookup_oui(mac):
	manufacturer = 'Unknown'
	mac = mac.replace(':','')
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

PARSE_STATE_AP = 0
PARSE_STATE_STATION = 1

f = open('/home/pi/defcon/sensor_properties', 'r')
sensor_name = f.readline()
sensor_name = sensor_name[0:len(sensor_name)-1]

c = pycurl.Curl()
c.setopt(c.CONNECTTIMEOUT, 5)
c.setopt(c.TIMEOUT, 8)
c.setopt(c.FAILONERROR, True)

db = sqlite3.connect('/home/pi/defcon/sensor_log.db')
cur = db.cursor()

try:
	c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/sensor_log.json')
	c.setopt(c.POSTFIELDS, "{\"event\": \"Start 802.11 Scan\", \"sensor\": \"" + sensor_name + "\", \"event_time\": \"" + time.strftime("%m/%d/%y %H:%M:%S") + "\"}" )
	c.perform()
	cur.execute("INSERT INTO events VALUES (NULL, 1, 'Start 802.11 Scan', '" + sensor_name + "', '" + time.strftime("%m/%d/%y %H:%M:%S") + "')")
	db.commit()
except pycurl.error, error:
	cur.execute("INSERT INTO events VALUES (NULL, 0, 'Start 802.11 Scan', '" + sensor_name + "', '" + time.strftime("%m/%d/%y %H:%M:%S") + "')")
	db.commit()
	

db = sqlite3.connect('/home/pi/defcon/lwsensor-master/Live/80211.db')
cur = db.cursor()

#if __name__ == "__main__":
while(True):
	time.sleep(60*30)
	os.system("cp /home/pi/defcon/80211/ap_list-01.csv /home/pi/defcon/80211/tmp.csv")
	f = open('/home/pi/defcon/80211/tmp.csv')
	parse_state = PARSE_STATE_AP
	
	apCurlString = ('{"sensor": "' + sensor_name + '", "date": "' + time.strftime("%m/%d/%y %H:%M:%S") + '", "APs": {')
	stationCurlString = ('{"sensor": "' + sensor_name + '", "date": "' + time.strftime("%m/%d/%y %H:%M:%S") + '", "stations": {')
	
	for line in f:
		params = line.split(",")
		if(params[0] == 'BSSID'):
			parse_state = PARSE_STATE_AP
		elif(params[0] == 'Station MAC'):
			parse_state = PARSE_STATE_STATION
		else:
			if(parse_state == PARSE_STATE_AP and len(params) > 1):
				BSSID = str.strip(params[0])
				manufacturer = lookup_oui(BSSID)
				first_seen = str.strip(params[1])
				last_seen = str.strip(params[2])
				channel = str.strip(params[3])
				if(channel == '-1'):
					channel = 'Unknown'
				speed = str.strip(params[4])
				privacy = str.strip(params[5])
				cipher = str.strip(params[6])
				auth = str.strip(params[7])
				power = str.strip(params[8])
				beacon_count = str.strip(params[9])
				data_count = str.strip(params[10])
				ESSID_length = str.strip(params[12])
				ESSID = str.strip(params[13])
				ESSID = params[13].rstrip(' \t\r\n\0')

				if(ESSID_length == '1' or ESSID_length == '0'):
					ESSID = '--'

				apCurlString += '"' + BSSID + '":{ "BSSID":"' + BSSID + '","ESSID":"' + ESSID + '", "manufacturer":"' + manufacturer + '", "channel":"' + channel + '", "speed":"' + speed + '", "privacy":"' + privacy + '", "cipher":"' + cipher + '", "auth":"' + auth + '", "power":"' + power + '", "beacon_count":"' + beacon_count + '", "data_count":"' + data_count + '", "first_seen":"' + first_seen + '", "last_seen":"' + last_seen + '"}, ' 
				

			elif(parse_state == PARSE_STATE_STATION and len(params) > 1):
				BSSID = str.strip(params[0])
				manufacturer = lookup_oui(BSSID)
				first_seen = str.strip(params[1])
				last_seen = str.strip(params[2])
				power = str.strip(params[3])
				packet_count = str.strip(params[4])

				stationCurlString += '"' + BSSID + '":{ "BSSID":"' + BSSID + '", "manufacturer":"' + manufacturer + '", "power":"' + power + '", "packet_count":"' + packet_count + '", "first_seen":"' + first_seen + '", "last_seen":"' + last_seen + '"}, ' 
				

	os.system("rm -f /home/pi/defcon/tmp.csv")

	apCurlString = apCurlString[0:len(apCurlString)-2]
	apCurlString += '}}'
	stationCurlString = stationCurlString[0:len(stationCurlString)-2]
	stationCurlString += '}}'
	try:
		c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/ap_observations.json')
		c.setopt(c.POSTFIELDS, apCurlString)
		c.perform()
	except pycurl.error, error:
		n, s = error
		print(s)
	try:
		c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/station_observations.json')
		c.setopt(c.POSTFIELDS, stationCurlString)
		c.perform()
	except pycurl.error, error:
		n, s = error
		print(s)
	break
