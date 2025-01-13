################################################################
#Name: mab_alg
#Desc: Main file to run the Multi Armed Bandit(MAB) algorithms
################################################################
import socket
from general import *
from networking.ethernet import Ethernet
from networking.ipv4 import IPv4
from networking.icmp import ICMP
from scapy.all import *
from networking.tcp import TCP, TCP_flag
from networking.udp import UDP
from networking.pcap import Pcap
from networking.http import HTTP
from networking.pkt_info import *
from networking.epsilon_policy import *
from networking.ucb_policy import *
from networking.th_sampling_policy import *
from networking.random_policy import *
import time
from networking.monitor_path import *
#from scapy.all import sniff
import sys
import os
import subprocess as sub
import struct
import argparse

TAB_1 = '\t - '
TAB_2 = '\t\t - '
TAB_3 = '\t\t\t - '
TAB_4 = '\t\t\t\t - '

DATA_TAB_1 = '\t   '
DATA_TAB_2 = '\t\t   '
DATA_TAB_3 = '\t\t\t   '
DATA_TAB_4 = '\t\t\t\t   '
PROXY_IP     = "10.71.1.122"; PROXY_MAC     = "00:00:00:00:00:02"
CLOUD_IP     = "10.71.3.121"; CLOUD_MAC     = "00:1b:21:bf:6b:46"
INT_PROXY_IP = "10.71.4.122"; INT_PROXY_MAC = "00:1b:21:bf:6a:e6"
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
AWS_IP_1     ="3.232.19.221" ;AWS_IP_2   ="3.232.19.222" ;AWS_IP_3     ="3.232.19.223" ;AWS_IP_4     ="3.232.19.224"; AWS_IP_5     ="3.232.19.225" ;
TOKYO_AWS_IP_1     ="54.179.218.211" ;TOKYO_AWS_IP_2   ="54.179.218.212" ;TOKYO_AWS_IP_3     ="54.179.218.213" ;TOKYO_AWS_IP_4     ="54.179.218.214"; TOKYO_AWS_IP_5     ="54.179.218.215" ;
SOURCE_ARR = [SOURCE_IP_0, SOURCE_IP_1, SOURCE_IP_2, SOURCE_IP_3, SOURCE_IP_4]
TARGET_ARR = [EP_IP_0, EP_IP_1, EP_IP_2, EP_IP_3, EP_IP_4 ,AWS_IP_1,AWS_IP_2,AWS_IP_3,AWS_IP_4,AWS_IP_5,TOKYO_AWS_IP_1,TOKYO_AWS_IP_2,TOKYO_AWS_IP_3,TOKYO_AWS_IP_4,TOKYO_AWS_IP_5]
PARALLEL_FLOWS=1
PRIMARY_CLIENT_PORT=list(range(64000,66500,PARALLEL_FLOWS))
ALL_CLIENT_PORT=list(range(64000,66500))


## Define our Custom Action function
def custom_action(packet):
    # getting IP layer
    ip = packet.getlayer("IP")
    # getting TCP layer
    tcp = packet.getlayer("TCP")
    tcp_f=TCP_flag(tcp.fields['flags'].value)

    #print_pkt(packet, ip, tcp, tcp_f)
    pkt_update(packet,tcp,tcp_f,ip)

#update the pkt and send it when it finish to routing table to to set the path
def pkt_update(packet,tcp,tcp_f,ip):
    REVERSE_MODE=True
    if ((tcp_f.flag_syn) and (tcp_f.flag_ack)  and (packet.src in [CLOUD_MAC, INT_PROXY_MAC]) and (ip.fields["dst"] in SOURCE_ARR )
        and tcp.fields['dport'] not in PRIMARY_CLIENT_PORT): #temp fix for reverse mode
        first_byte= tcp.seq if REVERSE_MODE else tcp.ack
        pkt_table.create_entry(src_ip = ip.fields["dst"],src_port =tcp.fields['dport'], dest_ip =ip.fields["src"],dest_port =tcp.fields['sport'], size= 0, ts= ip.time,first_byte=first_byte)



    if ( ((tcp_f.flag_fin  and tcp_f.flag_ack) or  (tcp_f.flag_rst and tcp_f.flag_ack)) and
         (packet.src in [CLOUD_MAC, INT_PROXY_MAC]) and (ip.fields["dst"] in SOURCE_ARR ) ):
        #print_pkt(packet, ip, tcp, tcp_f)
        last_byte= tcp.seq if REVERSE_MODE else tcp.ack
        if (tcp.fields['dport'] not in PRIMARY_CLIENT_PORT): #change to support revers mode
            pkt_table.update_size_with_ack(dest_ip=ip.fields["src"], dest_port =tcp.fields['sport'],
                                           src_ip=ip.fields["dst"],src_port =tcp.fields['dport'], last_byte=last_byte)

        if (tcp.fields['dport'] not in ALL_CLIENT_PORT) : #close with iper3 control finish

            pkt = pkt_table.close_entry(dest_ip=ip.fields["src"], dest_port =tcp.fields['sport'],
                                           src_ip=ip.fields["dst"],src_port =tcp.fields['dport'], size=0, ts= ip.time)
            if (packet.src == CLOUD_MAC):
                path = "CLOUD"
            else:
                path = "INTERNET"
            if (pkt != "EMPTY_PKT"):
                route_table.update_table_policy(pkt, path)
                mon_table.add_path(ip.time, path,ip.fields["src"])


def print_pkt(packet,ip,tcp,tcp_f):
    if (ip.fields["dst"] in (SOURCE_ARR + TARGET_ARR) and
      (tcp_f.flag_syn  or   tcp_f.flag_fin or (tcp_f.flag_rst and tcp_f.flag_ack)) and
     ((tcp.fields['sport']  in ALL_CLIENT_PORT) or (tcp.fields['dport']  in ALL_CLIENT_PORT))):
        print('\nEthernet Frame:')
        print(TAB_1 + 'Protocol: {}, Source: {}, Target: {} time {}'.format("TCP", ip.fields["src"], ip.fields["dst"],
                                                                            ip.time))
        print(TAB_1 + 'Source MAC: {}, Destination MAC: {}'.format(packet.src, packet.dst))
        print(tcp.fields)
        print(TAB_1 + 'TCP Segment: \n')
        print(TAB_1 + 'Source port: {}, Destination port: {}'.format(tcp.fields['sport'], tcp.fields['dport']))
        print(TAB_2 + 'Flags:')
        print(TAB_3 + 'URG: {}, ACK: {}, PSH: {}'.format(tcp_f.flag_urg, tcp_f.flag_ack, tcp_f.flag_psh))
        print(TAB_3 + 'RST: {}, SYN: {}, FIN:{}'.format(tcp_f.flag_rst, tcp_f.flag_syn, tcp_f.flag_fin))
        if (packet.src == CLOUD_MAC):
            print(TAB_1 + 'RECEIVE PKT from CLOUD route time {}'.format(ip.time))
        elif (packet.src in [INT_PROXY_MAC]):
            print(TAB_1 + 'RECEIVE PKT from INTERNET route time {}'.format(ip.time))
        else:
            if (packet.dst == CLOUD_MAC):
                print(TAB_1 + 'SEND PKT through CLOUD route time {}'.format(ip.time))
            elif (packet.dst in [INT_PROXY_MAC]):
                print(TAB_1 + 'SEND PKT through INTERNET route time {}'.format(ip.time))

def main():
    # global data structure
    global route_table, mon_table, pkt_table
    #setting test run
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-path','--path', help='path folder for logs', required=False, default="./bin")
    parser.add_argument('-p','--policy', help='choose the Multi Armed Bandit policy [EPSILON_GREEDY/UCB/T_SAMPLING]', required=False, default="EPSILON_GREEDY")
    parser.add_argument('-m','--monitor', help='monitor for debug', required=False, default="MULTIPLE_FLOW")
    args = vars(parser.parse_args())
    
    path = args["path"]
    policy = args["policy"]
    monitor_type = args["monitor"]
    
    #Creating path folder
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    
    pkt_table   = pkt_table_t(policy) #includ all ongoing pktts
    mon_table = path_monitor_c(path, monitor_type)
    print("Start Multi Armed Bandit algorithm")
    if (policy == "EPSILON_GREEDY"):
        armed_bendit_type = "Round-Robin" if monitor_type == "SINGLE_FLOW" else "Random"
        route_table = epsilon_table_base_t(folder=(path), armed_b_type=armed_bendit_type)  # include all the paths
        print("Start algorithm  EPSILON_GREEDY policy ")
    elif (policy == "UCB"):
        route_table = ucb_table_base_t()  # include all the paths
        print("Start algorithm  UCB policy")
    elif (policy == "T_SAMPLING"):
        route_table = t_sample_table_base_t()  # include all the paths
        print("Start algorithm Thompson Sampling policy")
    elif (policy == "RANDOM"):
        route_table = random_table_base_t()  # include all the paths
        print("Start RANDOM policy")

    while 1:
        a = sniff(iface=[INF1NAME, INF2NAME], filter="tcp[tcpflags] & (tcp-syn | tcp-fin | (tcp-rst ) ) != 0", prn=custom_action, store=False)
        #print("scapy results:\n",a)

if __name__ == '__main__':

    main()


