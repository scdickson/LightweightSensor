import os
import time

#Start Bluetooth and Bluetooth LE scan
time.sleep(5)
os.system("sudo python /home/pi/defcon/bluetooth/bluetooth_scan.py &")

#Start wideband spectrum scan
time.sleep(5)
os.system("sudo python /home/pi/defcon/wideband/wideband_scan.py &")

#Start airodump-ng for 802.11 scan
time.sleep(5)
os.system("sudo rm -f /home/pi/defcon/80211/ap_list*")
os.system("sudo rm -f /home/pi/defcon/80211/tmp*")
os.system("sudo airmon-ng start wlan1")
time.sleep(10)
os.system("sudo airodump-ng mon0 -w /home/pi/defcon/80211/ap_list --band abg --output-format csv 2>/dev/null &")
os.system("sudo python /home/pi/defcon/80211/80211Parser.py &")

#Start data manager
time.sleep(5)
os.system("sudo python /home/pi/defcon/upload_manager.py &")
