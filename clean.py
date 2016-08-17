import sqlite3
import os
import time

db = sqlite3.connect('/home/pi/defcon/sensor_log.db')
cur = db.cursor()
cur.execute("DELETE FROM events")
db.commit()

db = sqlite3.connect('/home/pi/defcon/bluetooth/bluetooth.db')
cur = db.cursor()
cur.execute("DELETE FROM scan_result")
db.commit()

db = sqlite3.connect('/home/pi/defcon/wideband/wideband.db')
cur = db.cursor()
cur.execute("DELETE FROM scan_result")
db.commit()
os.system('sudo rm -f /home/pi/defcon/wideband/wbscan*')

os.system('sudo rm -f /home/pi/defcon/80211/*.csv')
