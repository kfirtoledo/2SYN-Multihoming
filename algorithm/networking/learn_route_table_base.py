#####################################################################################
#Name: lear_route_table_base
#Desc: This class contain all the function to manage the routing table for the MAB algorithms.
####################################################################################
from networking.pkt_info import *
import os
import subprocess
import time
from hurry.filesize import size as size_f

class route_table_base_t:
    def __init__(self, policy="EPSILON", folder=""):
        self.table = []
        self.policy = policy
        self.folder = folder
        dest_ip_arr =["10.71.2.123","10.71.2.124","10.71.2.125","5.180.211.133"]#,"10.71.2.126","10.71.2.127",
                      #"3.232.19.221", "3.232.19.222", "3.232.19.223", "3.232.19.224", "3.232.19.225",
                      #"54.179.218.211", "54.179.218.212", "54.179.218.213", "54.179.218.214", "54.179.218.215"]
        for dest_ip in dest_ip_arr:
            self.clear_path(dest_ip,"0")
            self.clear_path(dest_ip, "0")

        #CLEAN COMMAND
        self.set_first_route("10.71.2.0", "255.255.255.0")
        self.set_first_route("3.232.19.0", "255.255.255.0")
        self.set_first_route("54.179.218.0", "255.255.255.0")
        self.set_first_route("5.180.211.0", "255.255.255.0")

        cmd = "sudo iptables -t mangle -F"
        os.system(cmd)
        cmd = "sudo iptables  -F FORWARD"
        os.system(cmd)

    def update_table_policy(self, pkt, last_trans_path):
        exist_flag = 0
        #print("update_table_policy: pkt path {}".format(last_trans_path))
        for entry in self.table:
            if (pkt.dest_ip == entry.dest_ip):
                exist_flag = 1
                entry.update_item(last_trans_path, pkt.bw)
                self.choose_path(entry, last_trans_path)

        if (exist_flag == 0):
            self.adding_new_path(pkt, last_trans_path)

        #self.print_table()

    #only for new path setting the routing table to check different destination
    def adding_new_path(self, pkt, path):
        print("EMPTY FUNCTION")
        # rt = routing_item_t(path, pkt.bw, pkt.dest_ip)
        # self.table.append(rt)
        # print('ROTING_TABLE: adding NEW path to Routing Table  through {} to dest_ip {}'.format(path, pkt.dest_ip))
        # if (path == "CLOUD"):
        #     self.set_route_path("INTERNET", pkt.dest_ip)
        # else:
        #     self.set_route_path("CLOUD", pkt.dest_ip)

    def choose_path(self, entry, last_trans_path):
        print("EMPTY FUNCTION")
        # if (entry.nof_flow % 10 == 0) and (entry.path  == last_trans_path):#multi-armed benditsudo apt-get update check another path each 10
        #     print('ROTING_TABLE: Multi-Armed Bendit check')
        #     self.clear_path(entry.dest_ip)
        #     if (entry.path == "CLOUD"):
        #         self.set_route_path("INTERNET", entry.dest_ip)
        #     else:
        #         self.set_route_path("CLOUD", entry.dest_ip)
        #
        # elif ((entry.nof_flow % 10 == 1) or (entry.nof_flow % 10 == 2) or \
        #       (entry.nof_flow % 10 == 0) and (entry.path != last_trans_path)): #after the multi ambient set the path correctly
        #     self.clear_path(entry.dest_ip)
        #     self.set_route_path(entry.path, entry.dest_ip)
        #
        # else:
        #     print('ROTING_TABLE: NO update to dest_ip {} using {} rout'.format(entry.dest_ip, entry.path))


    def clear_path(self,dest_ip, metric="10"):
        #cmd = "sudo route del -net " + dest_ip + " netmask 255.255.255.255 metric " + metric + " ens1"
        #os.system(cmd)
        cmd = ["sudo", "route", "del", "-net", dest_ip, "netmask", "255.255.255.255","metric", metric, "ens1"]
        subprocess.run(cmd)

        #cmd = "sudo route del -net " + dest_ip + " netmask 255.255.255.255  metric" + metric + " ens2f0"
        #os.system(cmd)
        cmd = ["sudo", "route", "del", "-net", dest_ip, "netmask", "255.255.255.255","metric", metric, "ens2f0"]
        subprocess.run(cmd)
        #print('ROTING_TABLE: clear_path to dest_ip {} time {}'.format(dest_ip,time.time()))

    def set_route_path(self, path, dest_ip):
        if (path == "CLOUD"):
            #cmd = "sudo route add -net " + dest_ip + " netmask 255.255.255.255 metric 10 ens1"
            cmd = ["sudo", "route", "add", "-net", dest_ip, "netmask", "255.255.255.255", "metric","10", "ens1"]
        else:  # internet
            #cmd = "sudo route add -net " + dest_ip + " netmask 255.255.255.255 metric 10 ens2f0"
            cmd = ["sudo", "route", "add", "-net", dest_ip, "netmask", "255.255.255.255", "metric", "10", "ens2f0"]
        subprocess.run(cmd)
        #os.system(cmd)
        #print('ROTING_TABLE: set_path  through {} to dest_ip {}'.format(path, dest_ip))
    def print_table(self):
        print('EMPTY ROTING_TABLE_PRINT')

    def set_first_route(self, ip, mask):
        cmd = "sudo route add -net " + ip + " netmask " + mask + " metric 20 ens2f0"
        os.system(cmd)
        cmd = "sudo route del -net " + ip + " netmask " + mask + " ens1"
        os.system(cmd)
