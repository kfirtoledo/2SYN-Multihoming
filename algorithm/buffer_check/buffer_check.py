import signal
import subprocess
from datetime import datetime
from subprocess import Popen
from sys import argv
import re  # xu
import time
import json

run = True


def signal_handler(signal, frame):
    global run
    # print ("exiting")
    run = False


def save_to_json(file_name,json_file):
    with open(file_name, 'w') as outfile:
        json.dump(json_file, outfile)
        outfile.close()

def buffer_size_record(if_name,results_filename,tick_interval_accuracy):
    queue_len_bytes_dict = {}
    drops_dict = {}
    # queue_len_packets_list = []

    # Check if tick_interval_accuracy is between 0 to 4
    tick_interval_accuracy = tick_interval_accuracy
    print("tick_interval_accuracy: {} sec".format(tick_interval_accuracy))
    #assert tick_interval_accuracy<0 or tick_interval_accuracy>4, "accuracy (last parameter) should be a number between 0 to 4"

    signal.signal(signal.SIGINT, signal_handler)
    #output_file = open("q_disc_debug.txt", 'w')
    results_file = open(results_filename+".txt", 'w')
    results_file.write("%s\t\t%s %s %s\n" % ("Time", "Q_s[B]", "Q_s[Pkt]", "Drop[Pkt]"))
    last_dropped = 0
    while run:
        p = Popen(["/sbin/tc", "-s", "qdisc", "show", "dev", if_name], stdout=subprocess.PIPE,
                  universal_newlines=True)
        output = p.communicate()
        #output_file.write(output[0])
        # parse queue length
        #qdisc netem 2: parent 1: limit 1000 delay 50.0ms
        #Sent 31118396842 bytes 452242517 pkt (dropped 0, overlimits 0 requeues 0) 
        #backlog 0b 0p requeues 0

        match = re.search(r'dropped\s+(\d+).*backlog\s+(\d+[kK]?)b\s+(\d+)p', output[0], re.DOTALL)
        if match:
            drops_str = match.group(1)
            drops = int(drops_str) - last_dropped
            last_dropped = int(drops_str)
            if match.group(2).find("K") == -1:
                num_of_bytes = match.group(2)
            else:
                num = int(match.group(2)[0:-1]) * 1000
                num_of_bytes = str(num)
            num_of_packets = match.group(3)
            num_of_cut_digits = tick_interval_accuracy-6
            time_str = round(time.time(),3)
            results_file.write("%s\t%s\t%s\t%s\n" % (time_str, num_of_bytes, num_of_packets, drops_str))
            #queue_len_bytes_dict[datetime.now().strftime("%H:%M:%S.%f")[:num_of_cut_digits]] = "%s\t%s\t%d" % (
            #    num_of_bytes, num_of_packets, drops)
            queue_len_bytes_dict[time_str] = "%s\t%s\t%d" % (num_of_bytes, num_of_packets, drops)

            save_to_json(results_filename+".json",queue_len_bytes_dict)
            time_to_sleep = tick_interval_accuracy - tick_interval_accuracy *0.7
            time.sleep(time_to_sleep)

if __name__ == '__main__':
    assert argv != 4, "usage: tc_qdisc_implementation <ifName> <filename> <tick interval accuracy (0-4)>"
    if_name = "ens2"  # argv[1]
    results_filename = "buffer_check"  # argv[2]
    tick_interval_accuracy = 1  # argv[3]
    buffer_size_record(if_name, results_filename, tick_interval_accuracy)