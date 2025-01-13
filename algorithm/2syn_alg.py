################################################################
#Name: 2syn_alg
#Desc: Main file to run the 2SYN algorithm
################################################################
import socket
from scapy.all import *
from general import *
from networking.ethernet import Ethernet
from networking.ipv4 import IPv4
from networking.icmp import ICMP
from networking.tcp import TCP, TCP_flag
from networking.udp import UDP
from networking.pcap import Pcap
from networking.http import HTTP
from networking.routing_table import *
from networking.monitor_path  import *
from networking.cfg import *
import time,argparse
import sys

## Define our Custom Action function
def custom_action(packet):
    # getting IP layer
    start_m_time=time.time_ns()
    #print(f"Start function {time.time_ns()}")
    ip = packet.getlayer("IP")
    # print(TAB_1 + 'Destination: {}, Source: {}, Protocol: {}'.format(eth.dest_mac, eth.src_mac, eth.proto))
    # print(TAB_2 + 'Protocol: {}, Source: {}, Target: {}'.format(ipv4.proto, ipv4.src, ipv4.target))

    # getting TCP layer
    tcp = packet.getlayer("TCP")
    tcp_f=TCP_flag(tcp.fields['flags'].value)

    #check syn
    if (tcp_f.flag_ack and (tcp_f.flag_syn) and (packet.src in [CLOUD_MAC, INT_PROXY_MAC])
        and (ip.fields["dst"] in SOURCE_ARR) and tcp.fields['dport'] not in CLIENT_PORT):
        if (packet.src == CLOUD_MAC):
            kind = "CLOUD"
        if (packet.src == INT_PROXY_MAC):
            kind = "INTERNET"
        rt.check_SYN_exist(src_port = tcp.fields['dport'] ,  dest_ip =ip.fields["src"], src_ip =ip.fields["dst"], kind = kind, time_pkt=ip.time,start_m_time= start_m_time)
        #print_pkt(packet, ip, tcp, tcp_f)
    #update double_syn algorithm
    if (((tcp_f.flag_fin and tcp_f.flag_ack) or (tcp_f.flag_rst and tcp_f.flag_ack)) and  # rst for case server close connection before client
        (ip.fields["dst"] in SOURCE_ARR) and tcp.fields['dport']not in CLIENT_PORT) :  ##ignore incoming IP
        if (packet.src == CLOUD_MAC):
            kind = "CLOUD"
        if (packet.src == INT_PROXY_MAC):
            kind = "INTERNET"
        #print_pkt(packet, ip, tcp, tcp_f)
        rt.finish_packet_check(packet.src, ip.fields["src"], ip.fields["dst"], kind, ip.time)


        # update monitor path
        if kind in ["INTERNET","CLOUD"]:
            mon.add_path( ip.time, kind,  ip.fields["src"])
    # return f"Packet #{sum(packet_counts.values())}: {packet[0][1].src} ==> {packet[0][1].dst}"
def print_pkt(packet,ip,tcp,tcp_f):
    if (ip.fields["dst"] in (SOURCE_ARR + TARGET_ARR) and
            (tcp_f.flag_syn or tcp_f.flag_fin or (tcp_f.flag_rst and tcp_f.flag_ack)) and
            (tcp.fields['sport'] not in CLIENT_PORT or tcp.fields['dport'] not in CLIENT_PORT) and
            (tcp.fields['sport'] not in CLIENT_PORT or tcp.fields['dport'] not in CLIENT_PORT)):

        print('\nEthernet Frame:')
        print(TAB_1 + 'Protocol: {}, Source: {}, Target: {} time {}'.format("TCP", ip.fields["src"], ip.fields["dst"],
                                                                            ip.time))
        print(TAB_1 + 'Source MAC: {}, Destination MAC: {}'.format(packet.src, packet.dst))
        # print(TAB_2 + 'Sequence: {}, Acknowledgment: {}'.format(tcp.sequence, tcp.acknowledgment))
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
    print("Start Algorithm 1: 2SYN")
    # global data structure
    global rt, mon
    rt = routing_table()
    #setting test run
    parser = argparse.ArgumentParser(description='The 2SYN algorithm')
    parser.add_argument('-path','--path', help='path folder for logs', required=False, default="./bin")
    parser.add_argument('-m','--monitor', help='monitor for debug', required=False, default="MULTIPLE_FLOW")
    args = vars(parser.parse_args())
    
    path = args["path"]
    monitor_type = args["monitor"]
    
    #Creating path folder
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    
    mon = path_monitor_c(path ,monitor_type)
    
    while 1:
        a = sniff(iface=[INF1NAME, INF2NAME], filter="tcp[tcpflags] & (tcp-syn | tcp-fin | (tcp-rst ) ) != 0", prn=custom_action, store=False)

if __name__ == '__main__':

    main()