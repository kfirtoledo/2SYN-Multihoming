################################################################
#Name: epsilon_policy
#Desc: Contain the epsilon greedy algorithm for path selection
################################################################

from networking.learn_route_table_base import *
from networking.share_cfg import *
import time
import json
import random
class epsilon_rout_item_t(route_item_t):

    def __init__(self, path, bw, dest_ip,folder):
        super().__init__()
        self.dest_ip      = dest_ip
        self.current_path = path
        self.folder       = folder
        self.path_predict = {}
        self.nof_flow     = 0 #of the last path
        self.total_nof_flow = 0
        self.avg_cl_bw    = 0
        self.avg_int_bw   = 0
        self.update_bw_f(path, bw)

    def update_bw_f(self, path, bw):
        if (path == "CLOUD"):
            self.avg_cl_bw = bw
        else:
            self.avg_int_bw = bw
        self.nof_flow += 1
        self.total_nof_flow += 1
        self.save_bw_f()

    def save_bw_f(self):
        ts = time.time()
        self.path_predict.update({ts: ["cloud", self.avg_cl_bw, "internet", self.avg_int_bw, "choose_path", self.current_path]})
        json_path =self.folder + "path_predict_" + self.dest_ip
        with open(json_path, 'w') as outfile:
            json.dump( self.path_predict, outfile)
            outfile.close()

    def get_bw_f(self):
        if (self.current_path == "CLOUD"):
            return self.avg_cl_bw
        else:
            return self.avg_int_bw


    def reset_f(self, path, bw):
        self.current_path = path
        self.nof_flow  = 0
        self.update_bw_f(path, bw)

    def update_item(self, path, bw):
        avg_bw = self.get_bw_f()
        if (path == self.current_path):
            avg_bw = (avg_bw * self.nof_flow + bw) / (self.nof_flow + 1)
            self.update_bw_f(path, avg_bw)
            print('ROUTING_TABLE: use SAME path (EXPLOITING)  through {} to dest_ip {}, avg_bw {}, last_path bw {} nof_flow {} total_nof_flow {}'\
                .format(path, self.dest_ip, size_f(avg_bw), size_f(bw), self.nof_flow ,  self.total_nof_flow))
        else:
            if (path == "CLOUD"):
                switch_path = True if (bw > avg_bw * self.bw_factor) else False
            else: #(path == "INTERNET")
                switch_path = True if (bw * self.bw_factor > avg_bw ) else False

            if (switch_path == True):
                self.reset_f(path, bw)
                print('ROUTING_TABLE: SWITCH path (after EXPLORING) through {} to dest_ip {} previous avg_bw {}, last_path bw {} '.format(path, self.dest_ip, size_f(avg_bw), size_f(bw)))
            else:
                self.update_bw_f(path, bw) #updating the last bw of the other path
                print('ROUTING_TABLE: use SAME path(after EXPLORING) through {} to dest_ip {} avg_bw {}, last_path bw {} nof_flow {} total_nof_flow {}' \
                      .format(self.current_path, self.dest_ip, size_f(avg_bw), size_f(bw), self.nof_flow ,  self.total_nof_flow))

class epsilon_table_base_t(route_table_base_t):

    def __init__(self, folder='', armed_b_type="Round-Robin", policy="EPSILON"):
        super().__init__(policy, folder)
        self.epsilon_val = 5
        self.armed_b_type = armed_b_type
        print("policy ",policy,"type :",armed_b_type)
    #only for new path setting the routing table to check different destination
    def adding_new_path(self, pkt, path):
        rt = epsilon_rout_item_t(path, pkt.bw, pkt.dest_ip, self.folder)
        self.table.append(rt)
        #print('ROTING_TABLE: adding NEW path to Routing Table  through {} to dest_ip {}'.format(path, pkt.dest_ip, size_f(pkt.bw)))
        if (self.armed_b_type == "Round-Robin"):
            path = "INTERNET" if (path == "CLOUD") else "CLOUD"
        else:
            path = "INTERNET" if (random.uniform(0, 1) > 0.5) else "CLOUD" #random internet or cloud
        self.set_route_path(path, pkt.dest_ip)

    def choose_path(self, entry, last_trans_path):
        if (entry.nof_flow % self.epsilon_val == 0) and (entry.current_path  == last_trans_path):#multi-armed bendit check another path each epsilon
            print('ROTING_TABLE: Multi-Armed Bendit check: {} replace path {}'.format(entry.dest_ip,entry.current_path ))
            self.clear_path(entry.dest_ip)
            if (entry.current_path == "CLOUD"):
                self.set_route_path("INTERNET", entry.dest_ip)
            else:
                self.set_route_path("CLOUD", entry.dest_ip)

        elif ((entry.nof_flow % self.epsilon_val == 1) or (entry.nof_flow % self.epsilon_val == 2) or \
              (entry.nof_flow % self.epsilon_val == 0) and (entry.current_path != last_trans_path)): #after the multi ambient set the path correctly
            self.clear_path(entry.dest_ip)
            self.set_route_path(entry.current_path, entry.dest_ip)

        else:
            print('ROUTING_TABLE: NO update to dest_ip {} using {} rout'.format(entry.dest_ip, entry.current_path))
        #self.print_table()

    def print_table(self):
        print('')
        for entry in self.table:
                print(' ROUTING_TABLE_PRINT: path: {} ,CL_AVG_BW: {}, INT_AVG_BW: {}, DEST_IP:{}, number of flow: {}'
                      .format(entry.current_path, size_f(entry.avg_cl_bw),size_f(entry.avg_int_bw), entry.dest_ip, entry.nof_flow))