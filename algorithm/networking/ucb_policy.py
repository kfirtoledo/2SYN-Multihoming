################################################################
#Name: ucb_policy
#Desc: Contain the UCB algorithm for path selection
################################################################
from networking.learn_route_table_base import *
from networking.share_cfg import *
import math
class ucb_route_item_t(route_item_t):
#Check using not all history of UCB
    def __init__(self, path, dest_ip):
        super().__init__()
        self.last_path         = path
        self.dest_ip           = dest_ip
        self.avg_bw_cloud      = 0
        self.flow_num_cloud    = 1
        self.avg_bw_internet   = 0
        self.flow_num_internet = 1


    def update_item(self, path, bw):

        if (path == "CLOUD"):
            self.avg_bw_cloud = (self.avg_bw_cloud * self.flow_num_cloud + bw) / (self.flow_num_cloud + 1)
            self.flow_num_cloud += 1
        else:
            self.avg_bw_internet = (self.avg_bw_internet * self.flow_num_internet + bw) / (self.flow_num_internet + 1)
            self.flow_num_internet += 1
        self.last_path = path

class ucb_table_base_t(route_table_base_t):

    def __init__(self, policy="UCB1"):
        super().__init__(policy)

    #only for new path setting the routing table to check different destination
    def adding_new_path(self, pkt, path):
        rt = ucb_route_item_t(path,pkt.dest_ip)
        rt.update_item(path, pkt.bw)
        self.table.append(rt)
        print('ROTING_TABLE: adding NEW path to Routing Table  through {} to dest_ip {}'.format(path, pkt.dest_ip))
        if (path == "CLOUD"):
            self.set_route_path("INTERNET", pkt.dest_ip)
        else:
            self.set_route_path("CLOUD", pkt.dest_ip)

    def choose_path(self, entry, last_trans_path):
        const = 100
        cloud_q = entry.avg_bw_cloud       + const * math.sqrt(2 * math.log(entry.flow_num_cloud + entry.flow_num_internet) /entry.flow_num_cloud)
        internet_q = entry.avg_bw_internet + const * math.sqrt(2 * math.log(entry.flow_num_cloud + entry.flow_num_internet) /entry.flow_num_internet)
        self.clear_path(entry.dest_ip)
        if (cloud_q <= internet_q * entry.bw_factor):
            set_path = "INTERNET"
        else:
            set_path = "CLOUD"
        self.set_route_path(set_path, entry.dest_ip)
        print('ROTING_TABLE: CHOOSE_PATH  for dest ip {} path chosen{}   cloud_q {} internrt_q {} CLOUD_AVG_BW: {}, CLOUD_FLOW_NUM: {}, INTERNET_AVG_BW: {}, INTERNET_FLOW_NUM: {}'\
              .format(entry.dest_ip,set_path , cloud_q, internet_q, size_f(entry.avg_bw_cloud), entry.flow_num_cloud, size_f(entry.avg_bw_internet),entry.flow_num_internet))

    def print_table(self):
        print('ROTING_TABLE_PRINT')
        for entry in self.table:
            print('last_path: {}, DEST_IP:{},CLOUD_AVG_BW: {}, CLOUD_FLOW_NUM: {}, INTERNET_AVG_BW: {}, INTERNET_FLOW_NUM: {}'\
                  .format(entry.last_path, entry.dest_ip, size_f(entry.avg_bw_cloud), entry.flow_num_cloud, size_f(entry.avg_bw_internet),entry.flow_num_internet))

