# LightweightSensor

LightweightSensor is a project for DefCon 24 that collects Bluetooth, 802.11, and wideband scan information and displays results with a simple web interface. Data is periodically uploaded to Firebase by the sensor. If no Internet connection is available, results are stored in an sqlite database and uploaded at a later point.

To run the lightweight sensor, use the main.py script:
```
sudo python main.py
```

###### Hardware
![Hardware](https://raw.githubusercontent.com/scdickson/LightweightSensor/master/images/Hardware.jpg)

* Raspberry Pi 3
* Alfa Network 802.11 a/b/g/n adapter
* NooElec R820T2 SDR

###### Wideband Scan
![Wideband](https://raw.githubusercontent.com/scdickson/LightweightSensor/master/images/Wideband.png)
An RTL-SDR is used to perform a wideband scan from 75 MHz to 1700 MHz. A python script translates raw power levels into a waterfall plot.

###### 802.11 Data
![802.11](https://raw.githubusercontent.com/scdickson/LightweightSensor/master/images/80211Data.png)
802.11 channel, security, manufacturer, speed, and other information are gathered for APs as well as stations.

![ESSIDs](https://raw.githubusercontent.com/scdickson/LightweightSensor/master/images/ESSIDs.png)
ESSIDs along with their manufacturers and number of BSSIDs are tabulated.

![Mobile](https://raw.githubusercontent.com/scdickson/LightweightSensor/master/images/Mobile.png)
Mobile devices are enumerated by manufacturer.

###### Bluetooth Data
![MobileMAC](https://raw.githubusercontent.com/scdickson/LightweightSensor/master/images/MobileMAC.png)
Bluetooth devices are enumerated and compared with corresponding station MAC addresses. Android devices usually have the same Bluetooth and 802.11 MAC addresses while Apple devices usually have their Bluetooth and 802.11 MAC addresses offset by one.

###### Installation and Dependencies

Clone this repository and change the folder name to 'defcon'. Make sure the root folder is located at '/home/pi/defcon'. Install the following dependencies:

```
sudo raspi-config --expand-rootfs
sudo apt-get install -y git cmake
sudo apt-get install -y libpcap-dev
sudo apt-get install -y libusb-1.0-0-dev
sudo apt-get install -y python-pip
sudo apt-get install -y aircrack-ng
sudo apt-get install -y python-dev
sudo apt-get install -y libbluetooth-dev
sudo apt-get install -y sqlite3
sudo apt-get install -y libcurl
sudo apt-get install -y libssl-dev
sudo apt-get install -y libcurl4-openssl-dev
sudo apt-get install -y librtlsdr-dev
sudo pip install bluez
sudo pip install pycurl

git clone git://git.osmocom.org/rtl-sdr.git
cd rtl-sdr
mkdir build
cd build
cmake ..
make
sudo make install
```
