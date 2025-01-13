import os
from numpy import random
from udp_generation_function import *
import hashlib
global_folder = "/home/user/mininet/"
duration_arr = []
data_unit_arr= []
duration_save_arr= [10  ,100,10 ,10 ,1  ,10 ,10 ,10 ,1  ,10 ,100,10 ,1  ,100,10  ,10 ,1 ,1  ,10 ,10 ,10,10,1,10,1,10,10,10,10,10,1,1,10,10,10,1,100,10,10,100]
data_unit_save_arr= ["K","K","K","K","M","M","K","K","M","K","K","M","M","K","K","M","M","M","K","K","K","K","M","K","M","K","M","K","K","K","M","M","K","K","K","M","K","K","M","K"]
sleep_arr = []
#parameters
PARALLEL_PORT=1
BW_LIMIT = 120

class gen_param:
    def __init__(self, path,delay,num_hosts, num_tests,test_time,kind_generation,type_test,data_unit,udp,aws,bw_limit,
                 reverse_mode,with_terminate,type_terminate="drop"):
        self.path ="/home/user/mininet/exp/" + path
        self.delay     = delay
        self.num_hosts = num_hosts
        self.num_tests = num_tests
        self.test_time = test_time
        self.data_unit = data_unit
        self.kind_generation = kind_generation
        self.type_test = type_test
        self.udp = udp
        self.aws =aws
        self.with_terminate = with_terminate
        self.type_terminate = type_terminate
        self.bw_limit = bw_limit
        self.reverse_mode = reverse_mode


def create_generate_file(folder, file_name, num_hosts, test_time, sleep_val, test_loop,type_test,param,test_num, kind_gen="exp", first_run="no" ,aws=False,):
    output_folder = folder + "/test_generate"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if first_run == "yes":
        duration_arr.clear()
        data_unit_arr.clear()
        sleep_arr.clear()
        seed = int(hashlib.sha1(folder.encode("utf-8")).hexdigest(), 16) % (10 ** 8)
        print("folder {} seed: {}".format(folder, seed))
        random.seed(seed)
        random.seed(seed+1)

    for i in range(num_hosts):
        output_test = output_folder + "/host_test" + str(i + 115)
        if not os.path.exists(output_test):
            os.makedirs(output_test)
        f_name = output_test + file_name
        f = open(f_name, "w+")
        f.write("sudo rm -rf " + folder + "/result* \n")
        if (sleep_val > 0):
            start_sleep_val= (sleep_val/2) if ((sleep_val/2) >=4) else 4
            f.write("sudo sleep " + str(start_sleep_val * i ) + "\n")
        for j in range(test_loop):
            data_unit=param.data_unit
            if kind_gen == "exp":
                if (first_run == "yes"):
                    duration = round(random.exponential(scale=test_time, size=1)[0])
                    duration = 8 if duration < 8 else duration
                    #duration = 120 if duration > 120 else duration
                    duration = 40 if duration > 40 else duration
                    duration_arr.append(duration)
                else:
                    duration = duration_arr[i * test_loop + j]
            elif kind_gen == "web_search":
                if param.with_terminate:
                    duration = duration_save_arr[i * test_loop + j]
                    data_unit = data_unit_save_arr[i * test_loop + j]
                elif param.with_terminate== False:
                    duration = duration_save_arr[test_num]
                    data_unit = data_unit_save_arr[test_num]
                elif (first_run == "yes"):
                    val = random.uniform(0,1)
                    if val < 0.55:
                        duration = 10; data_unit = "K"
                    elif 0.55<= val < 0.62:
                        duration = 100;data_unit = "K"
                    elif 0.62 <= val < 0.80:
                        duration = 1; data_unit = "M"
                    else:
                        duration = 10; data_unit = "M"
                    duration_arr.append(duration)
                    data_unit_arr.append(data_unit)
                else:
                    duration = duration_arr[i * test_loop + j]
                    data_unit = data_unit_arr[i * test_loop + j]

            else:
                duration = test_time  # iperf flags : -N -Z  --omit 1  -A 3,3  -l 100
            test_var =" -t "+ str(duration) if type_test =="time" else " -n " + str(duration) + data_unit# "M"

            if param.reverse_mode:
                test_var =test_var +" -R "
            if param.reverse_mode ==False and aws == "gcp_dest1":
                test_var = test_var + " -b 10M "
            Parrallel_port =PARALLEL_PORT
            cport_n=64010+ (j + i*test_loop)*Parrallel_port
            if (aws == "gcp_dest3"):
                dest_ip = "34.102.83." + str(230+i)
            elif (aws == "gcp_dest1"):
                dest_ip = "5.180.211." + str(i + 133)

            elif (aws =="dest4"):
                dest_ip = "13.230.90." + str(i + 221)
            elif (aws =="dest2"):
                dest_ip = "54.179.218." + str(i + 211)
            elif aws =="dest5":
                dest_ip = "3.232.19." + str(i + 221)
            else:
                dest_ip = "10.71.2." + str(i + 123)

            iperf_flags=" -N -P "+ str(Parrallel_port)+ " --connect-timeout 10000ms" # --rcv-timeout 2000  -N -Z --omit 1
            if (param.bw_limit):
                iperf_flags +=" -b " + str(BW_LIMIT) + "M "
            if param.with_terminate and j == 0 and param.type_terminate != "traffic":
                if param.aws == False:
                    f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_300mb_cloud_path.sh\" \n")
                else:
                    f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_300mb_cloud_path_aws.sh\" \n")
                    f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_300mb_cloud_path_upload.sh\" \n")

            if ("random" in folder): #param.reverse_mode and
                if (random.uniform(0, 1) >= 0.5) or j in[8,7]:
                    f.write("sshpass -p \"123456\" ssh user@10.70.1.120 \"source /home/user/mininet/internet_set.csh\"\n")
                else:
                    f.write("sshpass -p \"123456\" ssh user@10.70.1.120 \"source /home/user/mininet/cloud_set.csh\"\n")
            f.write("sudo iperf3 -p 5001 -c " + dest_ip + test_var + " --cport "+str(cport_n)+" " + iperf_flags +" -J --logfile "+ folder + "/result" + str(i) + "_" + str(j) + ".json  \n")
            if (sleep_val > 0):
                if kind_gen == "exp":
                    if (first_run == "yes"):
                        sleep_time = round(random.exponential(scale=sleep_val / 2, size=1)[0])
                        sleep_time = 2 if sleep_time < 2 else sleep_time
                        sleep_time = 10 if sleep_time > 10 else sleep_time
                        sleep_arr.append(sleep_time)
                    else:
                        sleep_time = sleep_arr[i * test_loop + j]
                else:
                    sleep_time = sleep_val
                f.write("sudo sleep " + str(sleep_time) + "\n")
            if param.with_terminate:
                if j == (test_loop/(10/4)) :
                    if param.type_terminate =="traffic":
                        if param.reverse_mode:
                            f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_tcp_traffic_terminate_download.sh\" & \n")
                        else:
                            f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_tcp_traffic_terminate_upload.sh\" & \n")
                    else:
                        if (aws == False):
                            f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_30mb_cloud_path.sh\" \n")
                        else:
                            if param.reverse_mode:
                                f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_10mb_cloud_path.sh\" \n")
                            else:
                                f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_3mb_cloud_path_upload.sh\" \n")
                                f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_5mb_cloud_path.sh\" \n")
                        f.write("sudo sleep " + str(sleep_time) + "\n")

        f.write("sudo sleep " + str(sleep_time * 2) + " \n")
        if param.with_terminate:
            if param.type_terminate == "traffic":
                if param.reverse_mode:
                    f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/teminate_iperf3.sh\" \n")
                else:
                    f.write(
                        "sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/teminate_iperf3.sh\" \n")
            else:
                if param.aws == False:
                    f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_300mb_cloud_path.sh\" \n")
                else:
                    f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_300mb_cloud_path_aws.sh\" \n")
                    f.write("sshpass -p \"123456\" ssh user@10.70.1.121 \"source  ~/mininet/set_300mb_cloud_path_upload.sh\" \n")
        if (i == (num_hosts - 1)):
            f.write("source " + folder + "/copy_res.sh\n\n")
    f.close()

def create_udp_generate_file(folder, file_name,  test_time, sleep_val, test_loop,type_test,  kind_gen,kind_udp,aws):
    if kind_udp == "REAL_UDP":
        output_test = folder + "/test_generate/host_test121/"
    else:
        output_test = folder + "/test_generate/host_test120/"
    if not os.path.exists(output_test):
        os.makedirs(output_test)
    f_name = output_test +file_name
    f = open(f_name, "w+")
    if (sleep_val > 0):
        start_sleep_val = (sleep_val / 2) if ((sleep_val / 2) >= 2) else 2
        f.write("sudo sleep " + str(start_sleep_val * i) + "\n")
    sleep_if = "NONE"
    for j in range(test_loop):
        if kind_gen == "exp":
            duration = duration_arr[j]
        else:
            duration = test_time  # iperf flags : -N -Z  --omit 1  -A 3,3  -l  100
        if (sleep_val > 0):
            if kind_gen == "exp":
                sleep_time = sleep_arr[j]
            else:
                sleep_time = sleep_val
        #using real udp
        if (kind_udp =="REAL_UDP"):
            if (j< test_loop/3 ) or j > (test_loop/3 * 2):
                #duration = round(duration / 2)
                if type_test == "data":
                    duration = round(duration / 10)
                f.write("sudo sleep " + str(duration) + "\n")
                f.write("sudo sleep " + str(sleep_time) + "\n")
            else:
                if type_test == "data":
                    duration   = round(duration / 5) #slower when udp is on
                    sleep_time = round(sleep_time + 0.5) * 3
                test_var = " -t " + str(duration ) + " -b 1000Mb"
                test_var_sleep = " -t " + str(sleep_time) + " -b 1000Mb"
                # if (j == int(test_loop / 3)):
                #     test_var = " -t " + str(duration* (test_loop / 3)*1.5) + " -b 1000Mb"
                f.write("sudo iperf3 -u -p 5005 -c 10.71.2.123" + test_var+"\n")
                f.write("sudo iperf3 -u -p 5005 -c 10.71.2.123" + test_var_sleep + "\n")

        elif ((kind_udp =="CLOUD_SHUTDOWN") or kind_udp =="INTERNET_SHUTDOWN" ):#Drop_throughput
            th_shutdown(f, test_loop, j, duration, type_test, kind_gen, sleep_val, sleep_arr, aws,bw_limit =BW_LIMIT, type_shutdown=kind_udp)
        elif (kind_udp =="MULTIPLE_DROPS"):
            sleep_if=th_multiple_time_shutdown(f, test_loop, j, duration, type_test, kind_gen, sleep_val, sleep_arr, aws,freq=10,sleep_if=sleep_if)
        else:
            th_one_cloud_shutdown(f, test_loop, j, duration, type_test, kind_gen, sleep_val, sleep_arr, aws)
    f.write("sudo sleep " + str(sleep_time * 2) + " \n")

def create_test_run_file(folder, alg_folders,alg_cmd_arr,test_num,param):
    file_name = folder + "/run_test.csh"
    run_files_folder = folder + "/run_files/"
    if not os.path.exists(run_files_folder):
        os.makedirs(run_files_folder)
    f = open(file_name, "w+")
    star ="echo \"***********************************\"\n"
    meta_data=f"# num of hosts: {param.num_hosts}, num of tests: {param.num_tests}, delay: {param.delay}, test_time: {param.test_time}\
     type: {param.kind_generation} type_test {param.type_test} with_udp {param.udp}"
    timeout = param.num_tests * (param.delay+param.test_time) +1500
    f.write("#Start test {} with  parameters {}: \n".format(test_num, meta_data))
    f.write("{}echo \"Start servers on EPS\"\n".format(star))
    f.write("source /home/user/mininet/cloud_experiement/code/scripts/set_servers_eps.csh\n{}".format( star))  # open servers

    for idx,alg in enumerate(alg_folders):
        alg_cmd = alg_cmd_arr[idx]
        file_name= run_files_folder+"run"+ alg.replace("/","_") +".csh"
        f.write("source {}\n".format(file_name))
        create_alg_run_file(folder,file_name,alg,alg_cmd,test_num, timeout, param.udp)
        f.write("\n\n")


def create_alg_run_file(folder,file_name,alg,alg_cmd,test_num, timeout,with_udp):

    f = open(file_name, "w+")
    star ="echo \"***********************************\"\n"
    f.write("{}echo \"Start {} routing algorithm for test {}\"\n\n".format(star, alg, test_num))
    path= folder+alg
    if (with_udp != False):
        if with_udp == "REAL_UDP":
            f.write("sudo sshpass -p \"123456\" ssh user@10.70.1.121 \" source {}{}/generator_file_udp.txt \" &\n".format(folder,alg))
        else:
            f.write("sudo sshpass -p \"123456\" ssh user@10.70.1.120 \" source {}{}/generator_file_udp.txt \" &\n".format(folder, alg))
    if alg in ["/internet", "/cloud"]:
        f.write("sudo sshpass -p \"123456\" ssh user@10.70.1.120 \"source /home/user/mininet/{}_set.csh\"\n".format(alg))
    #elif "/double_syn" in alg:
    elif alg == "/double_syn":
        f.write("sudo sshpass -p \"123456\" ssh user@10.70.1.120 \" sudo python3.6 -u /home/user/mininet/Python-Packet-Sniffer/sniffer.py {}/  MULTIPLE_FLOW |tee {}/log.file \" &\n".format(
                path,path))
    elif alg == "/packet_pair":
        f.write("sudo sshpass -p \"123456\" ssh user@10.70.1.120 \" sudo python3.6 -u /home/user/mininet/Python-Packet-Sniffer/sniffer_pkt_pair.py {}/  MULTIPLE_FLOW |tee {}/log.file \" &\n".format(
                path,path))
    elif alg == "/random":
        print("not perform random")
    else:
        f.write("sudo sshpass -p \"123456\" ssh user@10.70.1.120 \" sudo python3.6 -u /home/user/mininet/Python-Packet-Sniffer/sniffer_armed_bandit.py {}/ {} MULTIPLE_FLOW |tee {}/log.file \" &\n".format(path,alg_cmd,path))


    f.write("sleep 8\n")
    f.write("sudo sshpass -p \"123456\" parallel-ssh -i -h ~/.pssh_hosts_files -t {} -A source {}{}/generator_file.txt\n".format(str(int(timeout)), folder,alg))
    f.write("sudo {}{}/copy_res.sh\n".format(folder,alg))
    f.write("echo \"Finish {} routing algorithm for test {} \"\n{}".format(alg, test_num,star))
    f.write("source /home/user/mininet/cloud_experiement/code/scripts/clean_alg.csh\n")
    f.write("{}echo \"Reset servers on EPS\"\n".format(star))
    f.write("source /home/user/mininet/cloud_experiement/code/scripts/set_servers_eps.csh\n{}".format(star))  # open servers
    f.write("\n\n")


def copy_files_to_severs(folder,num_hosts,alg_folders,udp):
    file_name = folder + "copy_gen.sh"
    f = open(file_name, "w+")
    for i in range(num_hosts):
        f.write("\n #Copy files to hosts{} \n".format(str(115+ i)))
        for alg in alg_folders:
            f.write("sudo sshpass -p \"123456\" ssh user@10.70.1." +str(115+ i) +" \"mkdir -p " + folder + alg +"\"\n")

            f.write("sudo sshpass -p \"123456\" scp -r "+ folder +alg +"/test_generate/host_test"+str(115+ i)+
                    "/generator_file.txt user@10.70.1." +str(115+ i) +":"+ folder + alg +"\n")
    for alg in alg_folders:
        # create path for run on proxy server
        f.write("sudo sshpass -p \"123456\" ssh user@10.70.1.120" + " \"mkdir -p " + folder + alg + "\"\n")
        # create path for run for cloud server TO UDP
        if udp == "REAL_UDP":
            f.write("sudo sshpass -p \"123456\" ssh user@10.70.1.121" + " \"mkdir -p " + folder + alg + "\"\n")
            f.write("sudo sshpass -p \"123456\" scp -r " + folder + alg + "/test_generate/host_test121/generator_file_udp.txt user@10.70.1.121"+
                ":" + folder + alg + "\n")
        elif udp != False:
            f.write("sudo sshpass -p \"123456\" scp -r " + folder + alg + "/test_generate/host_test120/generator_file_udp.txt user@10.70.1.120" +
                ":" + folder + alg + "\n")
    f.close()
    #excute file path
    os.system("sudo chmod -R 777 " + folder)
    os.chmod(file_name, 0o777)
    cmd = "" + file_name
    print(cmd)
    os.system(cmd)

def create_copy_res_files(folder,num_hosts,alg_folders):
        for alg in alg_folders:
            file_name = folder + alg + "/copy_res.sh"
            f = open(file_name, "w+")
            range_num= num_hosts - 1 if (num_hosts == 5) else num_hosts
            for i in range(range_num):
                f.write("sudo rm {}/result{}_*.json \n".format(folder + alg, str(i)))
                f.write("sudo sshpass -p \"123456\" scp -r  user@10.70.1." +str(115+ i) +":"+ folder + alg+ "/result"+ str(i)+"*.json " + folder + alg+ "/ \n")

            f.write("sudo rm {}/path_monitor* \n".format(folder + alg))
            f.write("sudo sshpass -p \"123456\" scp -r  user@10.70.1.120:" + folder + alg + "/path_monitor* " + folder + alg + "/ \n")
            f.close()
            os.chmod(file_name, 0o777)

def create_folder_run_file(folder,nof_test):
    file_name = folder + "/run_exp.csh"
    f = open(file_name, "w+")
    for i in range(nof_test):
        f.write("source {}/test{}/run_test.csh\n".format(folder,str(i)))
    f.close()


def create_generate_folder(path,test_num,param,alg_folders,alg_cmd_arr):
    # Learning Algorithm
    #kind_generation = "exp" ;ind_generation = "static" ;type_test = "time";type_test = "data"
    #,"/packet_pair"]
    #alg_folders = ["/packet_pair"]
    for alg in  alg_folders:
        first_run_arg = "yes" if alg_folders.index(alg) == 0 else "no"
        create_generate_file(path + alg, "/generator_file.txt", param.num_hosts, param.test_time, param.delay,
                         test_loop=param.num_tests,type_test=param.type_test,param=param, kind_gen=param.kind_generation,
                         first_run=first_run_arg,aws=param.aws,test_num=test_num)
        if (param.udp != False):
            create_udp_generate_file(path + alg, "/generator_file_udp.txt", param.test_time, sleep_val=param.delay, test_loop=param.num_tests,type_test=param.type_test,  kind_gen=param.kind_generation, kind_udp=param.udp,aws=param.aws)
    copy_files_to_severs(path, param.num_hosts, alg_folders,udp=param.udp)
    create_copy_res_files(path, param.num_hosts, alg_folders)
    # create run files
    create_test_run_file(path,alg_folders,alg_cmd_arr,test_num, param)

####################### Main###############################################
alg_folders= ["/internet", "/cloud", "/greedy", "/ucb", "/t_sample", "/random","/double_syn"]
alg_cmd_arr = ["INTERNET", "CLOUD", "EPSILON_GREEDY", "UCB", "T_SAMPLING", "RANDOM", "DOUBLE_SYN",
               "PACKET_PAIR"]  # DOUBLE_SYN is empty
#change RTT #120 and 160
alg_folders= ["/internet", "/cloud", "/random","/double_syn"]
alg_cmd_arr = ["INTERNET", "CLOUD", "RANDOM", "DOUBLE_SYN"]  # DOUBLE_SYN is empty
random.seed(12345)



#same RTT same bw with traffic #120 and 160

# alg_folders= ["/internet", "/cloud", "/random","/double_syn"]
# alg_cmd_arr = ["INTERNET", "CLOUD", "RANDOM", "DOUBLE_SYN"]  # DOUBLE_SYN is empty
# param = gen_param(path="same_rtt_with_traffic/pkt_10k_1_test/" ,delay=1,num_hosts=1, num_tests=1,test_time=10,kind_generation="static",type_test="data",
#                    data_unit="K",udp=False,aws=False,bw_limit=False,reverse_mode=True)
# param = gen_param(path="same_rtt_with_traffic/pkt_100k_1_test/" ,delay=1,num_hosts=1, num_tests=1,test_time=100,kind_generation="static",type_test="data",
#                    data_unit="K",udp=False,aws=False,bw_limit=False,reverse_mode=True)
# param = gen_param(path="same_rtt_with_traffic/pkt_1M_1_test/" ,delay=1,num_hosts=1, num_tests=1,test_time=1,kind_generation="static",type_test="data",
#                    data_unit="M",udp=False,aws=False,bw_limit=False,reverse_mode=True)
# param = gen_param(path="same_rtt_with_traffic/pkt_100M_1_test/" ,delay=1,num_hosts=1, num_tests=1,test_time=100,kind_generation="static",type_test="data",
#                    data_unit="M",udp=False,aws=False,bw_limit=False,reverse_mode=True)

# test_folder="diff_rtt" #diff rtt 120, 160 same Bw
# test_folder="same_rtt_diff_bw" #same RTT diff bw no traffic
#test_folder="same_rtt_diff_bw_with_traffic" #same RTT diff bw with traffic from 119 127 #sudo iperf3 -p 5001 -c 10.71.1.118  -b 40M -t 4000 #from 122  #30 MB #sudo iperf3 -p 5001 -c 10.71.1.119  -b 40M -t 4000 #from 121 #300 MB
#test_folder="same_rtt_diff_bw_with_traffic_small_buffer" #same RTT diff bw with traffic from 119 127 #sudo iperf3 -p 5001 -c 10.71.1.118  -b 40M -t 4000 #from 122  #30 MB
# #sudo iperf3 -p 5001 -c 10.71.1.119  -b 40M -t 4000 #from 121 #300 MB #buffer 4718590 # buffer 471859
#test_folder="same_rtt_diff_bw_same_small_buffer_with_tcp_traffic" #same RTT diff bw with traffic from 119 127 #sudo iperf3 -p 5001 -c 10.71.1.118  -t 4000 -b 30m -P 10 #from 122  #30 MB
#sudo iperf3 -p 5002 -c 10.71.1.118  -b 30M -P 10 -t 4000 #from 121 #300 MB buffer # 471859 for both
#test_folder="same_rtt_same_bw_with_tcp_traffic" #same RTT diff bw no traffic from 119 to 127 with revers #sudo iperf3 -p 5002 -c 10.71.1.118  -P 10 -t 4000 #from 121
# test_folder="same_rtt_same_bw_with_udp_traffic" #same RTT diff bw no traffic from 120 to 127 in reverse #"sudo iperf3 -p 5002 -c 10.71.2.127  -t 0 -b 300M -R -u"

# alg_folders= ["/internet", "/cloud", "/random","/double_syn"]
# alg_cmd_arr = ["INTERNET", "CLOUD", "RANDOM", "DOUBLE_SYN"]  # DOUBLE_SYN is empty
# #
# nof_test = 20
# for size in [[10,"K"],[100,"K"],[1,"M"],[100,"M"]]:
#     param = gen_param(path=f"{test_folder}/pkt_{size[0]}{size[1]}_1_test/" ,delay=1,num_hosts=1, num_tests=1,test_time=size[0],kind_generation="static",type_test="data",
#                         data_unit=size[1],udp=False,aws=False,bw_limit=False,reverse_mode=True,with_terminate=False)
#     for i in range(nof_test):
#         create_generate_folder(param.path + "test" + str(i)+"/" ,i,param,alg_folders,alg_cmd_arr)
#     create_folder_run_file(param.path,nof_test)

#with terminate
#test_folder="same_rtt_diff_bw_300_100_with_terminate_30_with_traffic" #sudo iperf3 -p 5001 -c 10.71.1.118  -b 40M -t 14000 -P 4 from 121
#from 122 sudo iperf3 -p 5001 -c 10.71.1.118  -b 100M -t 4000
#test_folder="same_rtt_diff_bw_300_60_with_terminate_30_with_traffic" #sudo iperf3 -p 5001 -c 10.71.1.118  -b 40M -t 14000 -P 4 from 121
#from 122 sudo iperf3 -p 5001 -c 10.71.1.118  -b 100M -t 4000
# test_folder="same_rtt_diff_bw_300_100_with_terminate_30_with_traffic_equal" #sudo iperf3 -p 5001 -c 10.71.1.118  -b 40M -t 14000 -P 4 from 121
# #from 122 sudo iperf3 -p 5001 -c 10.71.1.118  -b 100M -t 4000
# nof_test = 1
# for size in [[10,"K"],[100,"K"],[1,"M"],[100,"M"]]:
#     param = gen_param(path=f"{test_folder}/pkt_{size[0]}{size[1]}_1_test/" ,delay=0.3,num_hosts=1, num_tests=20,test_time=size[0],kind_generation="static",type_test="data",
#                         data_unit=size[1],udp=False,aws=False,bw_limit=False,reverse_mode=True,with_terminate=True)
#     for i in range(nof_test):
#         create_generate_folder(param.path + "test" + str(i)+"/" ,i,param,alg_folders,alg_cmd_arr)
#     create_folder_run_file(param.path,nof_test)
#

#gcp
#test_folder="gcp_lte_vs_wifi_target_dest1" #no traffic
# test_folder="gcp_lte_vs_wired" #same RTT diff bw no traffic
# test_folder="gcp_lte_vs_wired_small_target_dest1" #no traffic
#test_folder="gcp_lte_vs_wired_100M_target_dest1";reverse_mode=True  #no traffic
#test_folder="gcp_lte_vs_wired_100M_10m_target_dest1_upload";reverse_mode=False  #no traffic

# nof_test = 20
# for size in [[30,"M"]]:
#     param = gen_param(path=f"{test_folder}/pkt_{size[0]}{size[1]}_1_test/" ,delay=0.3,num_hosts=1, num_tests=1,test_time=size[0],kind_generation="static",type_test="data",
#                         data_unit=size[1],udp=False,aws="gcp_dest1",bw_limit=False,reverse_mode=reverse_mode,with_terminate=False)
#     for i in range(nof_test):
#         create_generate_folder(param.path + "test" + str(i)+"/" ,i,param,alg_folders,alg_cmd_arr)
#     create_folder_run_file(param.path,nof_test)


#gcp with terminate
#test_folder="gcp_lte_vs_wired_100mb_target_dest1_with_terminate_upload"  #sudo iperf3 -p 5002 -c 10.71.1.118  -b 20M -t 4000 -P5 from 121
#test_folder="gcp_lte_vs_wired_small_target_dest1_with_terminate" ;reverse_mode=True ;type_terminate="drop" #sudo iperf3 -p 5002 -c 10.71.1.118  -b 20M -t 4000 -P5 from 121
#test_folder="gcp_lte_vs_wired_10mb_target_dest1_with_terminate_upload" ;reverse_mode=False ;type_terminate="drop"  #sudo iperf3 -p 5002 -c 10.71.1.118  -b 2M -t 4000 -P5 from 121

#befir traffic chnage in 121 ens2/1 to 100/10mb  115 and 121 is cubic
#test_folder="gcp_lte_vs_wired_100mb_target_dest1_with_terminate_type_traffic" ;reverse_mode=True ;type_terminate="traffic" #sudo iperf3 -p 5002 -c 10.71.1.118   -t 4000 -P 10
test_folder="gcp_lte_vs_wired_10mb_target_dest1_with_terminate_type_traffic_upload"  ;reverse_mode=False ;type_terminate="traffic"
# #
nof_test = 1
for size in [[10,"M"],[30,"M"]]:
    param = gen_param(path=f"{test_folder}/pkt_{size[0]}{size[1]}_1_test/" ,delay=0.3,num_hosts=1, num_tests=20,
                      test_time=size[0],kind_generation="static",type_test="data",data_unit=size[1],udp=False,
                      aws="gcp_dest1",bw_limit=False,reverse_mode=reverse_mode,with_terminate=True,type_terminate=type_terminate)
    for i in range(nof_test):
        create_generate_folder(param.path + "test" + str(i)+"/" ,i,param,alg_folders,alg_cmd_arr)
    create_folder_run_file(param.path,nof_test)

#gcp web search
test_folder="gcp_lte_vs_wired_100M_target_dest1_web_search" #no traffic
# test_folder="gcp_lte_vs_wired_100M_target_dest1_upload_web_search" #no traffic
#test_folder="gcp_lte_vs_wired_10M_target_dest1_upload_web_search" #no traffic
# #
# nof_test = 40
# for size in [[10,"M"]]:
#     param = gen_param(path=f"{test_folder}/pkt_{size[0]}{size[1]}_1_test/" ,delay=0.3,num_hosts=1, num_tests=1,test_time=size[0],kind_generation="web_search",type_test="data",
#                         data_unit=size[1],udp=False,aws="gcp_dest1",bw_limit=False,reverse_mode=False,with_terminate=False)
#     for i in range(nof_test):
#         create_generate_folder(param.path + "test" + str(i)+"/" ,i,param,alg_folders,alg_cmd_arr)
#     create_folder_run_file(param.path,nof_test)

#gcp web serachwith terminate
#test_folder="gcp_lte_vs_wired_100mb_target_dest1_web_search_with_terminate" ;reverse_mode=True ;type_terminate ="drop"#sudo iperf3 -p 5002 -c 10.71.1.118  -b 20M -t 4000 -P5 from 121 #bbr
#test_folder="gcp_lte_vs_wired_10mb_target_dest1_with_web_search_terminate_upload";reverse_mode=False; type_terminate ="drop"  #sudo iperf3 -p 5002 -c 10.71.1.118  -b 2M -t 4000 -P5 from 121 #bbr
#test_folder="gcp_lte_vs_wired_100mb_target_dest1_web_search_with_terminate_type_traffic" ;reverse_mode=True ;type_terminate ="traffic"#
test_folder="gcp_lte_vs_wired_10mb_target_dest1_with_web_search_terminate_upload_type_traffic";reverse_mode=False; type_terminate ="traffic"  #sudo iperf3 -p 5002 -c 10.71.1.118  -b 2M -t 4000 -P5 from 1

nof_test = 1
for size in [[10,"M"]]:
     param = gen_param(path=f"{test_folder}/pkt_{size[0]}{size[1]}_1_test/" ,delay=0.3,num_hosts=1, num_tests=40,test_time=size[0],kind_generation="web_search",type_test="data",
                         data_unit=size[1],udp=False,aws="gcp_dest1",bw_limit=False,reverse_mode=reverse_mode,with_terminate=True,type_terminate=type_terminate)
     for i in range(nof_test):
         create_generate_folder(param.path + "test" + str(i)+"/" ,i,param,alg_folders,alg_cmd_arr)
     create_folder_run_file(param.path,nof_test)
















######## 5 hosts time
#param = gen_param(path="new_5host_5ep_10_sec_tests/" ,delay=1,num_hosts=5, num_tests=20,test_time=10,kind_generation="static",type_test="time",udp=False,aws=False)
#param = gen_param(path="new_5host_5ep_50_sec_tests/" ,delay=1,num_hosts=5, num_tests=20,test_time=50,kind_generation="static",type_test="time",udp=False,aws=False)


######## 5 hosts DATA
#param = gen_param(path="new_5host_5ep_200mb_20_tests_no_limit/" ,delay=4,num_hosts=5, num_tests=20,test_time=200,kind_generation="static",type_test="data",udp=False,aws=False)
#param = gen_param(path="new_5host_5ep_200mb_20_tests_no_limit_cloud_shutdown_10mb/" ,delay=4,num_hosts=5, num_tests=20,test_time=200,kind_generation="static",type_test="data",udp="CLOUD_SHUTDOWN",aws=False)

#param = gen_param(path="new_5host_5ep_10mb_50_tests/" ,delay=4,num_hosts=5, num_tests=50,test_time=10,kind_generation="static",type_test="data",udp=False,aws=False)
#param  = gen_param(path="new_5host_5ep_200mb_20_tests_with_udp/" ,delay=4,num_hosts=5, num_tests=20,test_time=200,kind_generation="static",type_test="data",udp=True,aws=False)


##dest2###
#param = gen_param(path="5host_5ep_200mb_aws_dest2_tests/" ,delay=4,num_hosts=5, num_tests=20,test_time=200,kind_generation="static",type_test="data",udp=False,aws="dest2")
#param = gen_param(path="new_10host_10ep_10s_aws_dest2_tests/" ,delay=1,num_hosts=5, num_tests=20,test_time=10,kind_generation="static",type_test="time",udp=False,aws="dest2")
#param = gen_param(path="new_10host_10ep_30s_aws_dest2_tests/" ,delay=1,num_hosts=5, num_tests=20,test_time=30,kind_generation="static",type_test="time",udp=False,aws="dest2")
#param = gen_param(path="new_10host_10ep_aws_dest2_100mb_20_tests/" ,delay=4,num_hosts=5, num_tests=20,test_time=100,kind_generation="static",type_test="data",udp=False,aws="dest2")
# param = gen_param(path="new_5host_5ep_aws_dest2_200mb_20_tests_no_bw_limit_forward/" ,delay=3,num_hosts=5, num_tests=20,test_time=200,kind_generation="static",type_test="data",udp=False,aws="dest2")
# param = gen_param(path="new_5host_5ep_aws_dest2_10K_60_tests_no_bw_limit_forward/" ,delay=0.5,num_hosts=5, num_tests=60,test_time=10,kind_generation="static",type_test="data",udp=False,aws="dest2")
#param = gen_param(path="new_3host_3ep_aws_dest2_2_proxy_200mb_20_tests_no_bw_limit_th_shutdown_50mb/" ,delay=1,num_hosts=3, num_tests=20,test_time=200,kind_generation="static",type_test="data",udp="CLOUD_SHUTDOWN",aws="dest2")
#param = gen_param(path="new_5host_5ep_aws_dest2_200mb_20_tests_no_bw_limit_th_shutdown_10mb_0_2_time/" ,delay=3,num_hosts=5, num_tests=20,test_time=200,kind_generation="static",type_test="data",udp="CLOUD_SHUTDOWN",aws="dest2")
#folder_name ="5host_5ep_200mb_aws_dest2_tests/";nof_flows =20 ; nof_tests = 4; type_of_test ="DATA";

# nof_test = 20
# for i in range(nof_test):
#     create_generate_folder(param.path + "test" + str(i)+"/" ,i,param,alg_folders,alg_cmd_arr)
# create_folder_run_file(param.path,nof_test)

#create_test_run_file(path, ["/test"+ str(i)+"/double_syn/"], i, 5, 20, 10, 50, "static")