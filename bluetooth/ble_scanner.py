# BLE scanner, based on https://code.google.com/p/pybluez/source/browse/trunk/examples/advanced/inquiry-with-rssi.py

# https://github.com/pauloborges/bluez/blob/master/tools/hcitool.c for lescan
# https://kernel.googlesource.com/pub/scm/bluetooth/bluez/+/5.6/lib/hci.h for opcodes
# https://github.com/pauloborges/bluez/blob/master/lib/hci.c#L2782 for functions used by lescan

# performs a simple device inquiry, followed by a remote name request of each
# discovered device


# TODO(adamf) make sure all sizes in the struct.pack() calls match the correct types in hci.h
# and that we're not padding with 0x0 when we should be using an unsigned short

# NOTE: Python's struct.pack() will add padding bytes unless you make the endianness explicit. Little endian
# should be used for BLE. Always start a struct.pack() format string with "<"

import os
import sys
import struct
import bluetooth._bluetooth as bluez
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


LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS=0x00
LE_RANDOM_ADDRESS=0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE=7
OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_PARAMETERS=0x000B
OCF_LE_SET_SCAN_ENABLE=0x000C
OCF_LE_CREATE_CONN=0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE=0x01
EVT_LE_ADVERTISING_REPORT=0x02
EVT_LE_CONN_UPDATE_COMPLETE=0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE=0x04

# Advertisment event types
ADV_IND=0x00
ADV_DIRECT_IND=0x01
ADV_SCAN_IND=0x02
ADV_NONCONN_IND=0x03
ADV_SCAN_RSP=0x04

f = open('/home/pi/defcon/sensor_properties', 'r')
sensor_name = f.readline()
sensor_name = sensor_name[0:len(sensor_name)-1]
bluetooth_addr = f.readline()

c = pycurl.Curl()
c.setopt(c.URL, 'https://ns-sniffer.firebaseio.com/ble_devices.json')
c.setopt(c.CONNECTTIMEOUT, 5)
c.setopt(c.TIMEOUT, 8)
c.setopt(c.FAILONERROR, True)

bdb = sqlite3.connect('/home/pi/defcon/bluetooth/bluetooth.db')
bc = bdb.cursor()


def printpacket(pkt):
    for c in pkt:
        sys.stdout.write("%02x " % struct.unpack("B",c)[0])
    print 

def get_packed_bdaddr(bdaddr_string):
    packable_addr = []
    addr = bdaddr_string.split(':')
    addr.reverse()
    for b in addr: 
        packable_addr.append(int(b, 16))
    return struct.pack("<BBBBBB", *packable_addr)

def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x'%i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

# BLE and bluetooth use the same disconnect command.
#def hci_disconnect(sock, reason=bluez.HCI_OE_USER_ENDED_CONNECTION):
#    pass
    
def hci_connect_le(sock, peer_bdaddr, interval=0x0004, window=0x004,
                   initiator_filter=0x0, peer_bdaddr_type=LE_RANDOM_ADDRESS, 
                   own_bdaddr_type=0x00, min_interval=0x000F, max_interval=0x000F,
                   latency=0x0000, supervision_timeout=0x0C80, min_ce_length=0x0001,
                   max_ce_length=0x0001):

#    interval = htobs(0x0004);
#        window = htobs(0x0004);
#        own_bdaddr_type = 0x00;
#        min_interval = htobs(0x000F);
#        max_interval = htobs(0x000F);
#        latency = htobs(0x0000);
#        supervision_timeout = htobs(0x0C80);
#        min_ce_length = htobs(0x0001);
#        max_ce_length = htobs(0x0001);
#
#        err = hci_le_create_conn(dd, interval, window, initiator_filter,
#                        peer_bdaddr_type, bdaddr, own_bdaddr_type, min_interval,
#                        max_interval, latency, supervision_timeout,
#                        min_ce_length, max_ce_length, &handle, 25000);
# uint16_t        interval;
#        uint16_t        window;
#        uint8_t         initiator_filter;
#        uint8_t         peer_bdaddr_type;
#        bdaddr_t        peer_bdaddr;
#        uint8_t         own_bdaddr_type;
#        uint16_t        min_interval;
#        uint16_t        max_interval;
#        uint16_t        latency;
#        uint16_t        supervision_timeout;
#        uint16_t        min_ce_length;
#        uint16_t        max_ce_length;    
    package_bdaddr = get_packed_bdaddr(peer_bdaddr)
    cmd_pkt = struct.pack("<HHBB", interval, window, initiator_filter, peer_bdaddr_type)
    cmd_pkt = cmd_pkt + package_bdaddr
    cmd_pkt = cmd_pkt + struct.pack("<BHHHHHH", own_bdaddr_type, min_interval, max_interval, latency,
                                     supervision_timeout, min_ce_length, max_ce_length)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_CREATE_CONN, cmd_pkt)
        

def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)

def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
    #print "toggle scan: ", enable
# hci_le_set_scan_enable(dd, 0x01, filter_dup, 1000);
# memset(&scan_cp, 0, sizeof(scan_cp));
 #uint8_t         enable;
 #       uint8_t         filter_dup;
#        scan_cp.enable = enable;
#        scan_cp.filter_dup = filter_dup;
#
#        memset(&rq, 0, sizeof(rq));
#        rq.ogf = OGF_LE_CTL;
#        rq.ocf = OCF_LE_SET_SCAN_ENABLE;
#        rq.cparam = &scan_cp;
#        rq.clen = LE_SET_SCAN_ENABLE_CP_SIZE;
#        rq.rparam = &status;
#        rq.rlen = 1;

#        if (hci_send_req(dd, &rq, to) < 0)
#                return -1;
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)
    #print "sent toggle enable"


def hci_le_set_scan_parameters(sock):
    #print "setting up scan"
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    #print "got old filter"

    SCAN_RANDOM = 0x01
    OWN_TYPE = SCAN_RANDOM
    SCAN_TYPE = 0x01
    
# pack all these
# uint8_t         type;
#        uint16_t        interval;
#        uint16_t        window;
#        uint8_t         own_bdaddr_type;
#        uint8_t         filter;

#        memset(&param_cp, 0, sizeof(param_cp));
#        param_cp.type = type;
#        param_cp.interval = interval;
#        param_cp.window = window;
#        param_cp.own_bdaddr_type = own_type;
#        param_cp.filter = filter;
#
#        memset(&rq, 0, sizeof(rq));

# #define OGF_LE_CTL              0x08
#        rq.ogf = OGF_LE_CTL;

# #define OCF_LE_SET_SCAN_PARAMETERS              0x000B
#        rq.ocf = OCF_LE_SET_SCAN_PARAMETERS;

#        rq.cparam = &param_cp;
# #define LE_SET_SCAN_PARAMETERS_CP_SIZE 7
#        rq.clen = LE_SET_SCAN_PARAMETERS_CP_SIZE;
#        rq.rparam = &status;
#        rq.rlen = 1;
# if (hci_send_req(dd, &rq, to) < 0)


    INTERVAL = 0x10
    WINDOW = 0x10
    FILTER = 0x00 # all advertisements, not just whitelisted devices
    # interval and window are uint_16, so we pad them with 0x0
    cmd_pkt = struct.pack("<BBBBBBB", SCAN_TYPE, 0x0, INTERVAL, 0x0, WINDOW, OWN_TYPE, FILTER)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_PARAMETERS, cmd_pkt)

def parse_events(sock, loop_count=50):
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    done = False
    results = []
    deviceList = []
    for i in range(0, loop_count):
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        if event == LE_META_EVENT:
            subevent, = struct.unpack("B", pkt[3])
            pkt = pkt[4:]
            if subevent == EVT_LE_ADVERTISING_REPORT:
                num_reports = struct.unpack("B", pkt[0])[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                    MAC = packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
		    if(MAC not in deviceList):
			local_name_len, = struct.unpack("B", pkt[report_pkt_offset + 11])
                    	name = pkt[report_pkt_offset + 12:report_pkt_offset + 12+local_name_len]
			if(len(name) <= 1):
				name = '--'
                     	report_data_length, = struct.unpack("B", pkt[report_pkt_offset + 9])
                    	report_pkt_offset = report_pkt_offset +  10 + report_data_length + 1
                    	rssi, = struct.unpack("b", pkt[report_pkt_offset -1])
			manufacturer = lookup_oui(MAC)
			deviceList.append(MAC)
			try:
				c.setopt(c.POSTFIELDS, "{\"MAC\": \"" + MAC + "\", \"name\": \"" + name + "\", \"manufacturer\": \"" + manufacturer + "\", \"RSSI\": \"" + str(rssi) + "\", \"time_detected\": \"" + time.strftime("%m/%d/%y %H:%M:%S") + "\", \"sensor\": \"" + sensor_name + "\"}")
				c.perform()
				bc.execute("INSERT INTO scan_result VALUES(NULL, 1, 1, '" + MAC + "', '" + name + "', '" + manufacturer + "', '" + str(rssi) + "', '', '" + time.strftime("%m/%d/%y %H:%M:%S") + "', '" + sensor_name + "')")
				bdb.commit()
			except pycurl.error, error:
				ei, es = error
				print es
				bc.execute("INSERT INTO scan_result VALUES(NULL, 0, 1, '" + MAC + "', '" + name + "', '" + manufacturer + "', '" + str(rssi) + "', '', '" + time.strftime("%m/%d/%y %H:%M:%S") + "', '" + sensor_name + "')")
				bdb.commit()

    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )

def le_handle_connection_complete(pkt):
    status, handle, role, peer_bdaddr_type = struct.unpack("<BHBB", pkt[0:5])
    device_address = packed_bdaddr_to_string(pkt[5:11])
    interval, latency, supervision_timeout, master_clock_accuracy = struct.unpack("<HHHB", pkt[11:])
    #print "status: 0x%02x\nhandle: 0x%04x" % (status, handle)
    #print "role: 0x%02x" % role
    #print "device address: ", device_address

dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
except:
    print "error accessing bluetooth device..."
    sys.exit(1)

#hci_le_set_scan_parameters(sock)
#hci_enable_le_scan(sock)
#hci_disable_le_scan(sock)
#hci_connect_le(sock, "e5:e2:4a:56:53:54")
hci_connect_le(sock, bluetooth_addr);
parse_events(sock)
