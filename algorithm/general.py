
################################################################
#Name: general
#Desc: general setting for lab experiments
################################################################
import textwrap
from networking.cfg import *

# Returns MAC as string from bytes (ie AA:BB:CC:DD:EE:FF)
def get_mac_addr(mac_raw):
    byte_str = map('{:02x}'.format, mac_raw)
    mac_addr = ':'.join(byte_str).upper()
    return mac_addr


# Formats multi-line data
def format_multi_line(prefix, string, size=80):
    size -= len(prefix)
    if isinstance(string, bytes):
        string = ''.join(r'\x{:02x}'.format(byte) for byte in string)
        if size % 2:
            size -= 1
    return '\n'.join([prefix + line for line in textwrap.wrap(string, size)])


TAB_1 = '\t - '
TAB_2 = '\t\t - '
TAB_3 = '\t\t\t - '
TAB_4 = '\t\t\t\t - '

DATA_TAB_1 = '\t   '
DATA_TAB_2 = '\t\t   '
DATA_TAB_3 = '\t\t\t   '
DATA_TAB_4 = '\t\t\t\t   '

#PROXY_IP     = "10.71.1.122"; PROXY_MAC     = "00:00:00:00:00:02"
CLOUD_IP     = INF1IP; CLOUD_MAC     = INF1MAC
INT_PROXY_IP = INF2IP; INT_PROXY_MAC = INF2MAC
SOURCE_IP_0  = "10.71.1.115"; SOURCE_MAC    = "A4:5D:36:11:7A:59"
SOURCE_IP_1  = "10.71.1.116"; SOURCE_MAC = "00:00:00:00:00:8"
SOURCE_IP_2  = "10.71.1.117"; SOURCE_MAC = "00:00:00:00:00:9"
SOURCE_IP_3  = "10.71.1.118"; SOURCE_MAC = "00:00:00:00:00:10"
SOURCE_IP_4  = "10.71.1.119"; SOURCE_MAC = "00:00:00:00:00:11"
EP_IP_0      = "10.71.2.123"; EP_MAC_0   = "00:00:00:00:00:17"
EP_IP_1      = "10.71.2.124"; EP_MAC_1   = "00:00:00:00:00:18"
EP_IP_2      = "10.71.2.125"; EP_MAC_2   = "00:00:00:00:00:19"
EP_IP_3      = "10.71.2.126"; EP_MAC_3   = "00:00:00:00:00:20"
EP_IP_4      = "10.71.2.127"; EP_MAC_4   = "00:00:00:00:00:21"
SOURCE_ARR = [SOURCE_IP_0, SOURCE_IP_1, SOURCE_IP_2, SOURCE_IP_3, SOURCE_IP_4]
TARGET_ARR = [EP_IP_0, EP_IP_1, EP_IP_2, EP_IP_3, EP_IP_4 ]
CLIENT_PORT=list(range(64000,66500))