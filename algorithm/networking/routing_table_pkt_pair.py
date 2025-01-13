#####################################################################################
#Name: routin_table_pkt_pair
#Desc: The random_policy for using pkt_pair algorithm for selecting the path.
####################################################################################
import struct
import os
import sys
import subprocess
import hashlib
import time as time_f
import gc

class routing_table_t:

    def __init__(self, src_ip, dest_ip,src_port):
        self.src_port =src_ip
        self.dest_ip = dest_ip
        self.src_port = src_port
        self.time_1_syn_cl       = 0
        self.time_2_syn_cl       = 0
        self.time_1_syn_intr     = 0
        self.time_2_syn_intr     = 0
        self.time_1_syn_intr     = 0
        self.time_1_syn_ack_cl   = 0
        self.time_2_syn_ack_cl   = 0
        self.time_1_syn_ack_intr = 0
        self.time_2_syn_ack_intr = 0
        self.last_pkt_ack_syn_cl   = None
        self.last_pkt_ack_syn_intr = None
        self.pkt_pair_done =False
        self.kind = ""
        self.flow_count = 1

    def update_syn(self, kind,time):
        if kind == "CLOUD":
            if self.time_1_syn_cl == 0:
                self.time_1_syn_cl = time
            elif self.time_2_syn_cl == 0 :
                self.time_2_syn_cl = time
            else:
               print("ERROR: too much SYN dest_ip {} kind {} time {}".format(self.dest_ip, self.kind, time))
        else:
            if self.time_1_syn_intr == 0:
                self.time_1_syn_intr = time
            elif self.time_2_syn_intr == 0 :
                self.time_2_syn_intr = time
            else:
               print("ERROR: too much SYN dest_ip {} kind {} time {}".format(self.dest_ip, self.kind, time))

    def update_syn_ack(self, kind,time ,packet):
        if kind == "CLOUD":
            if self.time_1_syn_ack_cl == 0:
                self.time_1_syn_ack_cl = time
            elif self.time_2_syn_ack_cl == 0 :
                self.time_2_syn_ack_cl = time
                self.last_pkt_ack_syn_cl = packet
                if (self.time_2_syn_ack_intr != 0): self.pkt_pair_done = True
            else:
               print("ERROR: too much SYN ACK  dest_ip {} kind {} time {}".format(self.dest_ip, kind, time))


        else:
            if self.time_1_syn_ack_intr == 0:
                self.time_1_syn_ack_intr = time
            elif self.time_2_syn_ack_intr == 0 :
                self.time_2_syn_ack_intr = time
                self.last_pkt_ack_syn_intr = packet
                if (self.time_2_syn_ack_cl != 0): self.pkt_pair_done = True
            else:
               print("ERROR: too much SYN ACK  dest_ip {} kind {} time {}".format(self.dest_ip, kind, time))

    def calc_route(self):
        cl_time = (self.time_2_syn_ack_cl - self.time_1_syn_ack_cl ) - (self.time_2_syn_cl- self.time_1_syn_cl)

        print("cl_time {}\n     time_2_syn_ack_cl {}\n     time_1_syn_ack_cl {}\n         time_2_syn_cl {}\n         time_1_syn_cl {}"\
            .format(cl_time, self.time_2_syn_ack_cl,self.time_1_syn_ack_cl,self.time_2_syn_cl,self.time_1_syn_cl))

        intr_time = (self.time_2_syn_ack_intr -self.time_1_syn_ack_intr ) - (self.time_2_syn_intr - self.time_1_syn_intr)
        print("intr_time {}\n     time_2_syn_ack_intr {}\n     time_1_syn_ack_intr {}\n         time_2_syn_intr {}\n         time_1_syn_intr {}" \
              .format(intr_time, self.time_2_syn_ack_intr, self.time_1_syn_ack_intr, self.time_2_syn_intr, self.time_1_syn_intr))
        self.kind = "CLOUD" if cl_time <= intr_time else "INTERNET"
        print("CALC ROUTING: choose for dest_ip {} to route through kind {} ".format(self.dest_ip, self.kind))

    def update_flow_count(self):
        self.flow_count += 1
    def print(self):
        print("dest_ip {}, kind {},time {} ,flow_count {}".format(self.dest_ip, self.kind,self.flow_count))

class routing_table:

    def __init__(self, ):
        self.routing_table = {}
        self.max_flow_count = 3
        cmd = "sudo route del -net 10.71.2.0 netmask 255.255.255.0 ens2"
        self.do_cmd(cmd)
        cmd = "sudo route del -net 10.71.2.0 netmask 255.255.255.0 ens1"
        self.do_cmd(cmd)
        #CLEAN COMMAND
        cmd = "sudo iptables -t mangle -F"
        self.do_cmd(cmd)
        cmd = "sudo iptables  -F FORWARD"
        self.do_cmd(cmd)


        dest_ip_arr =["10.71.2.123","10.71.2.124","10.71.2.125","10.71.2.126","10.71.2.127"]
        src_ip_arr = ["10.71.1.115", "10.71.1.116", "10.71.1.117", "10.71.1.118", "10.71.1.119"]
        for idx, dest_ip in enumerate( dest_ip_arr):
            cmd = "sudo route add -net " + dest_ip + " netmask 255.255.255.255  metric 20 ens2"
            self.do_cmd(cmd)
            self.clean_routing(dest_ip,"CLOUD","10")
            self.clean_routing(dest_ip, "INTERNET", "10")
            self.clean_reject_farwarding(dest_ip,"CLOUD")
            self.clean_reject_farwarding(dest_ip,"INTERNET")
            self.add_pre_routing(dest_ip,src_ip_arr[idx],"CLOUD")
            self.drop_ep_pkts(dest_ip)

    def update_syn_in_rt_table(self, dest_ip,src_ip,src_port,kind, time):
        #ts=time_f.time()
        element= self.routing_table.get(dest_ip)
        if element != None :
            if (element.src_port == src_port):
                element.update_syn(kind,time)
                #print('ROTING_TABLE: Routing path already exist through {} to dest_ip {},'.format(element.kind,element.dest_ip))
            else:
                print('ERROR:Get SYN to dest_ip {} and port {} but path already exist with port {}'.format(element.dest_ip,src_port,element.src_port ))
        else:
            rt =routing_table_t(src_ip, dest_ip,src_port)
            rt.update_syn(kind, time)
            self.routing_table.update({dest_ip: rt })
            #finish_time = time_f.time()
            #print('ROTING_TABLE: UPDATING path  through {} to dest_ip {} start time {} finish time {} update time {}'.format(kind, dest_ip,ts,finish_time, finish_time -ts))

    def update_syn_ack_in_rt_table(self, dest_ip, src_ip,src_port, kind, time ,packet):
        element = self.routing_table.get(dest_ip)
        if element != None:
            if (element.src_port == src_port):
                element.update_syn_ack(kind, time ,packet)
                if element.pkt_pair_done and element.kind == "":
                    element.calc_route()
                    self.update_routing(dest_ip, src_ip, element.kind)
                    pkt_rt = element.last_pkt_ack_syn_cl if element.kind == "CLOUD" else element.last_pkt_ack_syn_intr
                    return element.pkt_pair_done, pkt_rt
            else:
                print('ERROR:Get ACK- SYN to dest_ip {} and port {} but path already exist with port{}'.\
                      format(element.dest_ip, src_port, element.src_port))
        else:
            print('ERROR: SYN_ACK receive with no SYN before path  through {}  to dest_ip {}'.format(kind, dest_ip))
        return False ,packet

    def finish_packet_check(self, src_port, dest_ip, src_ip, kind, time):
        print('finish_packet_check: finish sending flow through {} to dest_ip {}'.format(kind, dest_ip))
        element = self.routing_table.get(dest_ip)
        if element != None:
            if (int(element.src_port) <= int(src_port)):
                self.prepare_pkt_pair_check(dest_ip, src_ip, element.kind)
                self.routing_table.pop(dest_ip)
                gc.collect()
                return True
            else:
                print('ERROR:Get old FIN dest_ip {} and port {} but path already exist with port{}'. \
                      format(element.dest_ip, src_port, element.src_port))
        return False
    def update_routing(self, dest_ip,src_ip, kind):
        if (kind == "CLOUD"):
            #change routing
            cmd = ["sudo","route","add", "-net", dest_ip ,"netmask", "255.255.255.255","metric","10","ens1"]
            self.do_sub_process_cmd(cmd)

            cmd1 = ["sudo", "iptables", "-I", "FORWARD", "-p", "tcp", "-i", "ens2","-o","eno2","-s",dest_ip,
                     "-j", "REJECT","--reject-with", "tcp-reset"]
            self.do_sub_process_cmd(cmd1)
        else:
            cmd = ["sudo", "route", "add", "-net", dest_ip, "netmask", "255.255.255.255", "metric", "1", "ens2"]
            self.do_sub_process_cmd(cmd)
            cmd1 = ["sudo", "iptables", "-I", "FORWARD", "-p", "tcp", "-i", "ens1","-o","eno2","-s",dest_ip,
                     "-j", "REJECT", "--reject-with", "tcp-reset"]
            self.do_sub_process_cmd(cmd1)
            #print('Control message: UPDATING table start -updating internet path ')


        #Remove Extra routing
        if (kind == "CLOUD"):
            #self.clean_routing(dest_ip, "INTERNET","20")
            pass
        else:
            self.clean_routing(dest_ip, "CLOUD","10")
            cmd = ["sudo", "route", "add", "-net", dest_ip, "netmask", "255.255.255.255", "metric", "20", "ens2"]
            self.do_sub_process_cmd(cmd)
            #self.clean_routing(dest_ip, "INTERNET", "5")

        #Remove duplication
        self.clean_routing_duplication(dest_ip,src_ip, "CLOUD")
        self.clean_routing_duplication(dest_ip,src_ip, "INTERNET")
        cmd = ["sudo", "iptables", "-D", "FORWARD", "-p", "tcp", "-o", "eno2", "-s", dest_ip,
                "-j", "DROP"]
        self.do_sub_process_cmd(cmd)
        #cmd2 = ["sudo", "iptables", "-L", "-n", "-v"]
        #self.do_sub_process_cmd(cmd2)

    def clean_routing(self, dest_ip,kind,metric=""):
        if (kind == "CLOUD"):
            #cmd = "sudo route del -net " + dest_ip + " netmask 255.255.255.255 metric "+ metric +" ens1"
            cmd = ["sudo","route","del", "-net", dest_ip ,"netmask", "255.255.255.255","metric",metric,"ens1"]
        else:
            #cmd = "sudo route del -net " + dest_ip + " netmask 255.255.255.255 metric "+ metric +" ens2"
            cmd = ["sudo", "route", "del", "-net", dest_ip, "netmask", "255.255.255.255", "metric", metric, "ens2"]
        #self.do_cmd(cmd)
        self.do_sub_process_cmd(cmd)

    def prepare_pkt_pair_check(self, dest_ip, src_ip,kind):
        if (kind == "CLOUD"):
            self.add_pre_routing(dest_ip,src_ip ,"INTERNET")
            self.clean_reject_farwarding(dest_ip, "INTERNET")
        else:
            self.add_pre_routing(dest_ip,src_ip, "CLOUD")
            self.clean_reject_farwarding(dest_ip, "CLOUD")
        self.drop_ep_pkts(dest_ip)
        #print("Control message: PREPARE_SYN_CHECK ", kind, "\n")

    def add_pre_routing(self, dest_ip,src_ip ,kind):
        #print("Control message: ADD_PRE_ROUTING\n")
        if (kind == "CLOUD"):
            #cmd = "sudo iptables -t mangle -A PREROUTING -d "+ dest_ip +"/32 -j TEE --gateway 10.71.3.121"
            self.clean_routing(dest_ip, "INTERNET", "1")
            cmd = ["sudo", "iptables", "-t", "mangle", "-A", "PREROUTING", "-d", dest_ip + "/32", "-j", "TEE","--gateway", "10.71.3.121"]
        else:
            #cmd = "sudo iptables -t mangle -A PREROUTING -d "+ dest_ip +"/32 -j TEE --gateway 10.71.4.122"
            cmd = ["sudo", "iptables", "-t", "mangle", "-A", "PREROUTING", "-d", dest_ip + "/32", "-j", "TEE","--gateway", "10.71.4.122"]
        self.do_sub_process_cmd(cmd)

        # cmd = ["sudo", "iptables", "-t", "mangle", "-A", "PREROUTING", "-s", dest_ip + "/32", "-j", "TEE",
        #        "--gateway", src_ip]
        # self.do_sub_process_cmd(cmd)
        #self.do_cmd(cmd)

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
        else:
            cmd = ["sudo", "iptables", "-D","FORWARD", "-p", "tcp", "-i", "ens2", "-o", "eno2", "-s", dest_ip ,
                   "-j", "REJECT", "--reject-with", "tcp-reset"]

        self.do_sub_process_cmd(cmd)

    def drop_ep_pkts(self, dest_ip):
        cmd = ["sudo", "iptables", "-I", "FORWARD", "-p", "tcp", "-o", "eno2", "-s", dest_ip,
               "-j", "DROP"]
        self.do_sub_process_cmd(cmd)

    def do_cmd(self,cmd):
        os.system(cmd)
        #print("Control message: "+ cmd)

    def do_sub_process_cmd(self, cmd):
        subprocess.run(cmd)
#        print("Control message sub_process: " + " ".join(cmd))
