#####################################################################################
#Name: routing_table
#Desc: This class contain all the function to manage the routing table for the 2SYN algorithm.
####################################################################################
import struct
import os
import sys
import subprocess
import hashlib
import time as time_f
from networking.share_cfg import *

class routing_table_t(route_item_t):

    def __init__(self, src_port, dest_ip, kind, time):
        super().__init__()
        self.src_port = src_port
        self.dest_ip = dest_ip
        self.kind = kind
        self.time = time
        self.flow_count = 1

    def update_flow_count(self):
        self.flow_count += 1
    def print(self):
        print("dest_ip {}, kind {},time {} ,flow_count {}".format(self.dest_ip, self.kind, self.time,self.flow_count))

class routing_table:

    def __init__(self, ):
        self.routing_table = {}
        self.last_src_port = {}
        self.max_flow_count = 2
        self.clean_ip_net("10.71.2.0", "255.255.255.0")
        self.clean_ip_net("34.102.83.0","255.255.255.0")

        #CLEAN COMMAND
        cmd = "sudo iptables -t mangle -F"
        self.do_cmd(cmd)
        cmd = "sudo iptables  -F FORWARD"
        self.do_cmd(cmd)

        dest_ip_arr =["10.71.2.123","10.71.2.124","10.71.2.125","34.102.83.230","5.180.211.133"]
        src_ip_arr = ["10.71.1.115", "10.71.1.116", "10.71.1.117","10.71.1.115","10.71.1.115"] 

        for idx, dest_ip in enumerate( dest_ip_arr):
            cmd = "sudo route add -net " + dest_ip + " netmask 255.255.255.255  metric 20 ens2f0"
            self.do_cmd(cmd)
            self.do_cmd(cmd)
            self.clean_routing(dest_ip,"CLOUD","10")
            self.clean_routing(dest_ip, "INTERNET", "10")
            self.clean_reject_farwarding(dest_ip,"CLOUD")
            self.clean_reject_farwarding(dest_ip,"INTERNET")
            self.add_pre_routing(dest_ip,src_ip_arr[idx],"CLOUD")
            self.last_src_port.update({dest_ip : 0})

    def check_SYN_exist(self, src_port, dest_ip,src_ip, kind, time_pkt,start_m_time):
        update_flag = 1
        start_m_time = time_f.time()
        element= self.routing_table.get(dest_ip)
        if (element != None) :
        # for element in self.routing_table:
            if ((element.dest_ip == dest_ip) & (element.time < time_pkt)  ):
                update_flag = 0
                #print('ROTING_TABLE: Routing path already exist through {} to dest_ip {},'.format(element.kind,element.dest_ip))
        if (src_port <= self.last_src_port[dest_ip]): #fix bug in haproxy
            update_flag = 0
        if (update_flag):
            self.update_host_table(src_port, dest_ip,src_ip, kind, time_pkt)
            finish_tim = time_f.time()
            self.routing_table.update({dest_ip: routing_table_t(src_port, dest_ip, kind, time_pkt)})
            self.last_src_port[dest_ip] = src_port
        
            print(f"finish function {finish_tim- start_m_time}")
            print('ROTING_TABLE: UPDATING path  through {} to dest_ip {} '.format(kind, dest_ip))
    def finish_packet_check(self, src_port, dest_ip, src_ip, kind, time):
        element = self.routing_table.get(dest_ip)
        if element != None:
            element.update_flow_count()
            #print("dest_ip {} elemet flow count {}".format(dest_ip,element.flow_count))
            if element.flow_count >= self.max_flow_count:
                self.prepare_syn_check(dest_ip, src_ip, element.kind)
                self.routing_table.pop(dest_ip)
    def update_host_table(self, src_port, dest_ip,src_ip, kind, time):
        if (kind == "CLOUD"):
            #change routing
            cmd = ["sudo","route","add", "-net", dest_ip ,"netmask", "255.255.255.255","metric","10","ens1"]
            self.do_sub_process_cmd(cmd)

            cmd1 = ["sudo", "iptables", "-I", "FORWARD", "-p", "tcp", "-i", "ens2f0","-o","eno2","-s",dest_ip,
                    #"-j",  "REJECT", "--reject-with", "tcp-reset"]
                    "-j", "DROP"]#, "--reject-with", "tcp-reset"]
            self.do_sub_process_cmd(cmd1)
            msg='Control message: UPDATING table start -updating Cloud path '
        else:
            #cmd = "sudo route add -net "+ dest_ip +" netmask 255.255.255.255 metric 5 ens2f0"
            #self.do_cmd(cmd)
            cmd = ["sudo", "route", "add", "-net", dest_ip, "netmask", "255.255.255.255", "metric", "1", "ens2f0"]
            self.do_sub_process_cmd(cmd)
            cmd1 = ["sudo", "iptables", "-I", "FORWARD", "-p", "tcp", "-i", "ens1","-o","eno2","-s",dest_ip,
                    #"REJECT", "--reject-with", "tcp-reset"]
                    "-j", "DROP"]
            self.do_sub_process_cmd(cmd1)

            msg='Control message: UPDATING table start -updating internet path '

        #Remove Extra routing
        if (kind == "CLOUD"):
            #self.clean_routing(dest_ip, "INTERNET","20")
            a=3
        else:
            self.clean_routing(dest_ip, "CLOUD","10")
            cmd = ["sudo", "route", "add", "-net", dest_ip, "netmask", "255.255.255.255", "metric", "20", "ens2f0"]
            self.do_sub_process_cmd(cmd)
            #self.clean_routing(dest_ip, "INTERNET", "5")

        #Remove duplication
        self.clean_routing_duplication(dest_ip,src_ip, "CLOUD")
        self.clean_routing_duplication(dest_ip,src_ip, "INTERNET")
        print(msg)
    def clean_routing(self, dest_ip,kind,metric=""):
        if (kind == "CLOUD"):
            #cmd = "sudo route del -net " + dest_ip + " netmask 255.255.255.255 metric "+ metric +" ens1"
            cmd = ["sudo","route","del", "-net", dest_ip ,"netmask", "255.255.255.255","metric",metric,"ens1"]
        else:
            #cmd = "sudo route del -net " + dest_ip + " netmask 255.255.255.255 metric "+ metric +" ens2f0"
            cmd = ["sudo", "route", "del", "-net", dest_ip, "netmask", "255.255.255.255", "metric", metric, "ens2f0"]
        #self.do_cmd(cmd)
        self.do_sub_process_cmd(cmd)

    def prepare_syn_check(self, dest_ip, src_ip,kind):
        if (kind == "CLOUD"):
            self.add_pre_routing(dest_ip,src_ip ,"INTERNET")
            self.clean_reject_farwarding(dest_ip, "INTERNET")
        else:
            self.add_pre_routing(dest_ip,src_ip, "CLOUD")
            self.clean_reject_farwarding(dest_ip, "CLOUD")
        #print("Control message: PREPARE_SYN_CHECK ", kind, "\n")

    def add_pre_routing(self, dest_ip,src_ip ,kind):
        #print("Control message: ADD_PRE_ROUTING\n")
        if (kind == "CLOUD"):
            self.clean_routing(dest_ip, "INTERNET", "1")
            cmd = ["sudo", "iptables", "-t", "mangle", "-A", "PREROUTING", "-d", dest_ip + "/32", "-j", "TEE","--gateway", "10.71.3.121"]
        else:
            cmd = ["sudo", "iptables", "-t", "mangle", "-A", "PREROUTING", "-d", dest_ip + "/32", "-j", "TEE","--gateway", "10.71.4.122"]
        self.do_sub_process_cmd(cmd)

        cmd = ["sudo", "iptables", "-t", "mangle", "-A", "PREROUTING", "-s", dest_ip + "/32", "-j", "TEE",
               "--gateway", src_ip]
        self.do_sub_process_cmd(cmd)

    def clean_routing_duplication(self, dest_ip,src_ip, kind):
        if (kind == "CLOUD"):
            cmd = ["sudo", "iptables", "-t", "mangle", "-D", "PREROUTING", "-d", dest_ip + "/32", "-j", "TEE", "--gateway", "10.71.3.121"]
            self.do_sub_process_cmd(cmd)
            cmd = ["sudo", "iptables", "-t", "mangle", "-D", "PREROUTING", "-s", dest_ip + "/32", "-j", "TEE",
               "--gateway", src_ip]
            self.do_sub_process_cmd(cmd)
        else:
            cmd = ["sudo", "iptables", "-t", "mangle","-D", "PREROUTING", "-d", dest_ip + "/32", "-j","TEE", "--gateway", "10.71.4.122"]
            self.do_sub_process_cmd(cmd)
            cmd = ["sudo", "iptables", "-t", "mangle", "-D", "PREROUTING", "-s", dest_ip + "/32", "-j", "TEE",
               "--gateway", src_ip]
            self.do_sub_process_cmd(cmd)

    def clean_reject_farwarding(self, dest_ip,kind):
        #print("Control message: clean_reject_farwarding\n")
        if (kind == "CLOUD"):
            cmd = ["sudo", "iptables", "-D", "FORWARD","-p", "tcp",  "-i", "ens1", "-o", "eno2", "-s", dest_ip ,
                   "-j", "REJECT", "--reject-with", "tcp-reset"]
#                    "-j", "DROP"]
        else:
            cmd = ["sudo", "iptables", "-D","FORWARD", "-p", "tcp", "-i", "ens2f0", "-o", "eno2", "-s", dest_ip ,
                   "-j","REJECT", "--reject-with", "tcp-reset"]
#                   "-j", "DROP"]
        self.do_sub_process_cmd(cmd)

    def clean_ip_net(self,ip,mask):
        cmd = "sudo route del -net " + ip + " netmask " + mask + " ens2f0"
        self.do_cmd(cmd)
        cmd = "sudo route del -net " + ip + " netmask " + mask + " ens1"
        self.do_cmd(cmd)

    def do_cmd(self,cmd):
        os.system(cmd)
        #print("Control message: "+ cmd)

    def do_sub_process_cmd(self, cmd):
        subprocess.run(cmd)
        print("Control message sub_process: " + " ".join(cmd))
