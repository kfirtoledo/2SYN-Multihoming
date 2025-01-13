#####################################################################################
#Name: random_policy
#Desc: The random_policy algorithm for selecting the path randomly.
####################################################################################
from networking.learn_route_table_base import *
import time
import json
import random
class random_rout_item_t:

    def __init__(self, path, dest_ip,folder):
        self.dest_ip      = dest_ip
        self.current_path = path
        self.folder       = folder

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


    def update_item(self, path, bw):
        self.current_path =path

class random_table_base_t(route_table_base_t):

    def __init__(self, folder='', policy="RANDOM"):
        super().__init__(policy, folder)
        path = "INTERNET" if (random.random() > 0.5) else "CLOUD"  # random internet or cloud
        self.last_path=path
        if path == "CLOUD":
            print("start with cloud path")
            self.set_cloud_first_route("10.71.2.0", "255.255.255.0")
            self.set_cloud_first_route("5.180.211.0", "255.255.255.0")
        else:
            print("start with internet path")

    def adding_new_path(self, pkt, path):
        #rt = random_rout_item_t(path, pkt.dest_ip, self.folder)
        #self.table.append(rt) # not adding to tablr always add new path
        path = "INTERNET" if (random.uniform(0, 1) > 0.5) else "CLOUD" #random internet or cloud
        if path != self.last_path:
            self.clear_path(pkt.dest_ip)
            self.set_route_path(path, pkt.dest_ip)
            self.last_path = path
            print(f"Update to path {path}")
    def choose_path(self, entry, last_trans_path):
        path = "INTERNET" if (random.uniform(0, 1) > 0.5) else "CLOUD"  # random internet or cloud
        if path != self.last_path:
            self.clear_path(entry.dest_ip)
            self.set_route_path(path, entry.dest_ip)
            self.last_path=path
        print('ROTING_TABLE choose path: dest_ip {} using {} rout'.format(entry.dest_ip, path))
        #self.print_table()

    def print_table(self):
        print('')
        for entry in self.table:
                print(' ROTING_TABLE_PRINT: path: {} DEST_IP:{}'.format(entry.current_path,  entry.dest_ip))

    def set_cloud_first_route(self, ip, mask):
        cmd = "sudo route add -net " + ip + " netmask " + mask + " metric 20 ens1"
        os.system(cmd)
        cmd = "sudo route del -net " + ip + " netmask " + mask + " ens2f0"
        os.system(cmd)
