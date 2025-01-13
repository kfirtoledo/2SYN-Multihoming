import os
global_path="/home/user/mininet/"
def create_generate_file(folder,file_name, num,sleep_val,type=""):
    output_folder = global_path + folder
    print(output_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_name = output_folder + file_name
    f= open(file_name,"w+")
    f.write("sudo rm -rf " + "result* \n")
    if type:
        if (type == "CLOUD_TEST"):
            #f.write("h2 route add -net 10.0.0.0  netmask 255.255.255.0 metric 10 h2-eth2 \n")
            print("nothing")
        else:
            #f.write("xterm &\n")
            #f.write("" + type + "\n")
            print("nothing")
    for i in range(num):
        f.write("sudo iperf3 -p 5001 -c 10.71.2.123 -t 1 -J --logfile " + "./result" + str(i) + ".json \n")
        if (sleep_val > 0):
            f.write("sleep " + str(sleep_val)+"\n")
    f.write("sudo sshpass -p \"123456\" scp -r user@10.70.1.120:/home/user/mininet/"+ folder  +"/path_monitor.json . \n")
    f.close()

def create_exp_run_file(folder):
    file_name = global_path + folder +"/run_exp"
    f = open(file_name, "w+")
    f.write("sudo mn -c\n")
    f.write("sudo python3.6 cloud_topo.py " + folder + "/internet/generator_file.txt\n")
    f.write("sudo mn -c\n")
    f.write("sudo python3.6 cloud_topo.py " + folder + "/cloud/generator_file.txt CLOUD_TEST\n")

def create_folder_run_file(folder):
    file_name = global_path + folder +"/run_exp"
    f = open(file_name, "w+")
    f.write("source " + folder + "/exp_alg1/run_exp\n")
    f.write("source " + folder + "/exp_alg3/run_exp\n")

def create_generate_folder(path):
    #Double Syn Algorithm
    alg="sudo python3.6 ../../tools/Python-Packet-Sniffer/sniffer.py " + path +  "/exp_alg1/cloud/ &"
    delay     = 1
    num_tests = 20
    #referance
    create_generate_file(path + "/cloud", "/generator_file.txt", num_tests, delay, "CLOUD_TEST")
    create_generate_file(path + "/internet", "/generator_file.txt", num_tests, delay)
    #Double_SYN
    create_generate_file(path + "/double_syn"   , "/manual_generator_file.txt", num_tests, delay)
    create_generate_file(path + "/double_syn"   , "/generator_file.txt"       , num_tests, delay, alg)
    #GREADY algorithm
    alg = "sudo python3.6 ../../tools/Python-Packet-Sniffer/sniffer1.py "+ path + "/exp_alg3/cloud/ &"
    delay     = 1
    create_generate_file(path + "/gready"   , "/manual_generator_file.txt", num_tests, delay)
    create_generate_file(path + "/gready"   , "/generator_file.txt"       , num_tests, delay, alg)
    #UCB
    delay     = 1
    create_generate_file(path + "/ucb"   , "/manual_generator_file.txt", num_tests, delay)
    create_generate_file(path + "/ucb"   , "/generator_file.txt"       , num_tests, delay, alg)

    #Thomas Sampling
    delay     = 1
    create_generate_file(path + "/t_sampel"   , "/manual_generator_file.txt", num_tests, delay)
    create_generate_file(path + "/t_sampel"   , "/generator_file.txt"       , num_tests, delay, alg)
    #create run files
#    create_exp_run_file(path +"/exp_alg1")
#    create_exp_run_file(path + "/exp_alg3")
#    create_folder_run_file(path)



#create_generate_folder("exp/same_param")
create_generate_folder("exp/same_delay")
#create_generate_folder("exp/same_bw")
#create_generate_folder("exp/same_delay_nof")