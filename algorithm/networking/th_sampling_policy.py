################################################################
#Name: th_sampling_policy
#Desc: Contain the thompson sampling algorithm for path selection
################################################################
from networking.learn_route_table_base import *
from networking.share_cfg import *
import math
import numpy as np
class t_sample_route_item_t(route_item_t):

    def __init__(self, path, dest_ip):
        super().__init__()
        self.last_path         = path
        self.dest_ip           = dest_ip
        self.avg_bw_cloud      = 0
        self.flow_num_cloud    = 0
        self.a_cl = 2
        self.b_cl = 2
        self.avg_bw_internet   = 0
        self.flow_num_internet = 0
        self.a_int = 2
        self.b_int = 2
        np.random.seed(0)


    def update_item(self, path, bw):
        step= 0.5
        #step = 0.1
        if (path == "CLOUD"):
            self.avg_bw_cloud = (self.avg_bw_cloud * self.flow_num_cloud + bw) / (self.flow_num_cloud + 1)
            self.flow_num_cloud += 1
            #updating gamma distribution parameters

            if (bw >=  self.avg_bw_internet * self.bw_factor):
                self.a_cl += step
            else:
                self.b_cl += step
        else:
            self.avg_bw_internet = (self.avg_bw_internet * self.flow_num_internet + bw) / (self.flow_num_internet + 1)
            self.flow_num_internet += 1
            # updating gamma distribution parameters
            if (bw * self.bw_factor >= self.avg_bw_cloud):
                self.a_int += step
            else:
                self.b_int += step
        self.last_path = path

class t_sample_table_base_t(route_table_base_t):

    def __init__(self, policy="thompson_sampling"):
        super().__init__(policy)

    #only for new path setting the routing table to check different destination
    def adding_new_path(self, pkt, path):
        rt = t_sample_route_item_t(path,pkt.dest_ip)
        rt.update_item(path, pkt.bw)
        self.table.append(rt)
        print('ROTING_TABLE: adding NEW path to Routing Table  through {} to dest_ip {}'.format(path, pkt.dest_ip))
        if (path == "CLOUD"):
            self.set_route_path("INTERNET", pkt.dest_ip)
        else:
            self.set_route_path("CLOUD", pkt.dest_ip)

    def choose_path(self, entry, last_trans_path):
        print('thompson sampling choose_path')
        p_cl = np.random.beta(entry.a_cl, entry.b_cl)
        p_int = np.random.beta(entry.a_int, entry.b_int)


        self.clear_path(entry.dest_ip)
        if (p_cl <= p_int):
            self.set_route_path("INTERNET", entry.dest_ip)
        else:
            self.set_route_path("CLOUD", entry.dest_ip)

    def print_table(self):
        print('ROTING_TABLE_PRINT')
        for entry in self.table:
            print('last_path: {}, DEST_IP:{},CLOUD_AVG_BW: {}, CLOUD_FLOW_NUM: {}, INTERNET_AVG_BW: {}, INTERNET_FLOW_NUM: {}'.format(entry.last_path, entry.dest_ip, size_f(entry.avg_bw_cloud),
                                                                                                                                    entry.flow_num_cloud, size_f(entry.avg_bw_internet),entry.flow_num_internet))

