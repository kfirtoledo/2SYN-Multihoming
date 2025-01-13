################################################################
#Name: Monitor_path
#Desc: Contain  pat_monitor class for monitor the traffic 
################################################################
import json

class path_monitor_c:

    def __init__(self, json_path,flavor="SINGLE_FLOW"):
        self.path_mon  = {}
        self.flavor=flavor
        self.json_path = json_path + "/path_monitor.json"
        self.val=0

    def add_path(self, ts, path,src_ip):
        time = ts
        if (self.flavor =="SINGLE_FLOW"):
            self.path_mon.update({ts: path})
        else:
            self.val = self.val + 1
            self.path_mon.update({ self.val: [src_ip,path, ts]})

        #self.print()
        self.save_to_json()

    def print(self):
        print("\n\n\n PATH_MONITOR")
        print(self.path_mon)

    def save_to_json(self):
        with open(self.json_path, 'w') as outfile:
            json.dump(self.path_mon, outfile)
            outfile.close()

    def load_from_json(self):
        with open(self.json_path) as json_file:
         data = json.load(json_file)
        print(data)

