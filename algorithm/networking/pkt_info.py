#####################################################################################
#Name: pkt_info
#Desc: pkt_info class is abstraction for packet that contain all packet information.
####################################################################################
from hurry.filesize import size as size_f
import time
MAX_PKT_SIZE =0xFFFFFFFF
class pkt_t:

    def __init__(self,dest_ip,dest_port,src_ip,src_port, size, start_time, end_time, first_byte=0):

        self.size       = size
        self.start_time = start_time
        self.dest_ip    = dest_ip
        self.dest_port  = dest_port
        self.src_ip     = src_ip
        self.src_port   = src_port
        self.end_time   = end_time
        self.first_byte  = first_byte
        self.bw = 0

    def print(self):
        print(" TCP flow dest ip {} src ip{} total size: {}, start time {},end time {} BW {}".format(self.dest_ip ,self.src_ip, size_f(self.size), self.start_time, self.end_time,size_f( self.bw)))

    def finish(self, ts, size):
        self.size += size
        self.end_time = ts
        self.bw = self.size / (self.end_time - self.start_time)
        #self.print()

class pkt_table_t:

    def __init__(self,policy):
        self.pkt=[]
        self.policy=policy
    def create_entry(self, dest_ip,dest_port, src_ip,src_port, size, ts,first_byte=0):
        exist_flag = 0
        for p in self.pkt:
            if (dest_ip == p.dest_ip) and (src_ip == p.src_ip) and (dest_port == p.dest_port) and (src_port == p.src_port):
                exist_flag = 1
                print("CREATE_ENTRY already EXIST for dest IP : {} and src_ip {} time {}".format(dest_ip, src_ip, ts))

        if (not exist_flag):
            self.pkt.append(pkt_t(dest_ip,dest_port, src_ip,src_port, size, ts, 0,first_byte= first_byte))
            print("CREATE_ENTRY for dest IP : {} and src_ip {} time {} first_byte {}".format(dest_ip, src_ip, ts, first_byte))
        #print("create entry:")
        #self.print_table()

    def update_size(self, dest_ip, src_ip, size):
       for p in self.pkt:
        if (dest_ip == p.dest_ip) and (src_ip == p.src_ip):
            i = self.pkt.index(p)
            self.pkt[i].size = size + self.pkt[i].size

    def update_size_with_ack(self, dest_ip,dest_port, src_ip,src_port, last_byte):
       #print(f"inside update_size_with_ack {self.pkt}")
       for p in self.pkt:
           if (dest_ip == p.dest_ip) and (src_ip == p.src_ip) and (dest_port == p.dest_port) and (
                   src_port == p.src_port):
                i = self.pkt.index(p)
                self.pkt[i].size = last_byte - self.pkt[i].first_byte
                if self.pkt[i].size < 0 : #for case overlapping pkt field
                    self.pkt[i].size += MAX_PKT_SIZE
                #print(" TCP flow dest ip {} src ip{} update_size_with_ack : last_byte {}, first_byte {},  pkt size {}"\
                #      .format(dest_ip, src_ip, last_byte , self.pkt[i].first_byte, size_f(self.pkt[i].size)))
    def close_entry(self, dest_ip,dest_port, src_ip, src_port,size, ts):
        match=0
        for p in self.pkt:
            if (dest_ip == p.dest_ip) and (src_ip == p.src_ip) and (dest_port == p.dest_port) and (
                    src_port == p.src_port) and (p.size != 0): #remove for random
                rt_pkt =p
                self.pkt.remove(p)
                rt_pkt.finish(ts, size)
                #self.print_table()
                #print("CLOSE_ENTRY for dest IP : {} and src_ip {} time {}".format( p.dest_ip, p.src_ip,ts))
                return rt_pkt

        print("EMPTY_PKT for dest IP : {} and src_ip {} time {}".format(dest_ip,src_ip,time.time()))
        #self.print_table()
        return "EMPTY_PKT"
        #return (pkt_t(dest_ip, src_ip, size, ts, ts))

    def print_table(self):
        #print("Ongoing Pkt Table:")
        for p in self.pkt:
            p.print()