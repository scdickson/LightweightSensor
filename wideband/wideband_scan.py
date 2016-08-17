import os
import time
import pycurl
import sqlite3

lower_freq = '25M'
upper_freq = '1700M'
gain = '25'
bin_size = '1M'

client_id='09cde9e6884edc3'
client_secret='c24ae57604e0004c2fe17dba04a567aa1dad239a'

f = open('/home/pi/defcon/sensor_properties', 'r')
sensor_name = f.readline()
sensor_name = sensor_name[0:len(sensor_name)-1]

sldb = sqlite3.connect('/home/pi/defcon/sensor_log.db')
slc = sldb.cursor()

c = pycurl.Curl()
c.setopt(c.CONNECTTIMEOUT, 5)
c.setopt(c.TIMEOUT, 10)
c.setopt(c.FAILONERROR, True)

#curlParams = "curl -H \"Authorization: Client-ID " + client_id + "\" -F \"title=wbscan\" https://api.imgur.com/3/album"
#os.system(curlParams)

try:
	c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/sensor_log.json')
	c.setopt(c.POSTFIELDS, "{\"event\": \"Start Wideband Scan\", \"sensor\": \"" + sensor_name + "\", \"event_time\": \"" + time.strftime("%m/%d/%y %H:%M:%S") + "\"}" )
	c.perform()
	slc.execute("INSERT INTO events VALUES (NULL, 1, 'Start Wideband Scan', '" + sensor_name + "', '" + time.strftime("%m/%d/%y %H:%M:%S") + "')")
	sldb.commit()
except pycurl.error, error:
	slc.execute("INSERT INTO events VALUES (NULL, 0, 'Start Wideband Scan', '" + sensor_name + "', '" + time.strftime("%m/%d/%y %H:%M:%S") + "')")
	sldb.commit()

os.system("sudo rtl_power -f " + lower_freq + ":" + upper_freq + ":" + bin_size + " -i 120 -g " + gain + " -e 24h /home/pi/defcon/wideband/wbscan.csv &")

while True:
	time.sleep(60*50)
	current_time_millis = int(round(time.time() * 1000))
	os.system("sudo python /home/pi/defcon/wideband/heatmap.py /home/pi/defcon/wideband/wbscan.csv /home/pi/defcon/wideband/wbscan_" + str(current_time_millis) + ".png")
	curlParams = "curl -H \"Authorization: Client-ID " + client_id + "\" -H \"album: hjqu4\" -F image=@/home/pi/defcon/wideband/wbscan_" + str(current_time_millis) + ".png https://api.imgur.com/3/upload.xml"
	os.system(curlParams + " | python /home/pi/defcon/wideband/getImageID.py")
	time.sleep(20)
