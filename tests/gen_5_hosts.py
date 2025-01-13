import os
from numpy import random

global_folder = "/home/user/mininet/"
duration_arr = []
sleep_arr = []


def create_generate_file(folder, file_name, num_hosts, test_time, sleep_val, test_loop, kind_gen="exp", first_run="no"):
    output_folder = folder + "/test_generate"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if first_run == "yes":
        duration_arr.clear()
        sleep_arr.clear()
    for i in range(num_hosts):
        output_test = output_folder + "/host_test" + str(i + 115)
        if not os.path.exists(output_test):
            os.makedirs(output_test)
        f_name = output_test + file_name
        f = open(f_name, "w+")
        f.write("sudo rm -rf " + folder + "/result* \n")
        if (sleep_val > 0):
            f.write("sudo sleep " + str(sleep_val / 2 * i) + "\n")
        for j in range(test_loop):
            if kind_gen == "exp":
                if (first_run == "yes"):
                    duration = round(random.exponential(scale=test_time, size=1)[0])
                    duration = 10 if duration < 10 else duration
                    duration = 120 if duration > 120 else duration
                    duration_arr.append(duration)
                else:
                    duration = duration_arr[i * test_loop + j]
            else:
                duration = test_time  # iperf flags :  -l 100 -Z -A 3,3
            f.write("sudo iperf3 -p 5001 -c 10.71.2." + str(i + 123) + " -t " + str(
                duration) + " -N -Z --omit 1 -J --logfile " + folder + "/result" + str(i) + "_" + str(j) + ".json  \n")
            if (sleep_val > 0):
                if kind_gen == "exp":
                    if (first_run == "yes"):
                        sleep_time = round(random.exponential(scale=sleep_val / 2, size=1)[0])
                        sleep_time = 2 if sleep_time < 2 else sleep_time
                        sleep_arr.append(sleep_time)
                    else:
                        sleep_time = sleep_arr[i * test_loop + j]
                else:
                    sleep_time = sleep_val
                f.write("sudo sleep " + str(sleep_time) + "\n")
        f.write("sudo sleep " + str(test_time / 2) + " \n")
        if (i == (num_hosts - 1)):
            f.write("source " + folder + "/copy_res.txt\n\n")
    f.close()


def create_exp_run_file(folder):
    file_name = folder + "/run_exp"
    f = open(file_name, "w+")
    f.write("sudo mn -c\n")
    f.write("sudo python3.6 cloud_topo.py " + folder + "/internet/generator_file.txt\n")
    f.write("sudo mn -c\n")
    f.write("sudo python3.6 cloud_topo.py " + folder + "/cloud/generator_file.txt CLOUD_TEST\n")


def create_folder_run_file(folder):
    file_name = folder + "/run_exp"
    f = open(file_name, "w+")
    f.write("source " + folder + "/exp_alg1/run_exp\n")
    f.write("source " + folder + "/exp_alg3/run_exp\n")


def create_generate_folder(path):
    # # Double Syn Algorithm
    # alg = "sudo python3.6 ../../tools/Python-Packet-Sniffer/sniffer.py " + path + "/exp_alg1/cloud/ &"
    # delay = 10
    # num_tests = 1
    # num_hosts = 5
    # test_time = 40
    # create_generate_file(path + "/exp_alg1/alg", "/generator_file.txt", num_hosts, test_time, delay,
    #                      test_loop=num_tests, kind_gen="exp", first_run="yes")
    # create_generate_file(path + "/exp_alg1/cloud", "/generator_file.txt", num_hosts, test_time, delay,
    #                      test_loop=num_tests, kind_gen="exp", first_run="no")
    # create_generate_file(path + "/exp_alg1/internet", "/generator_file.txt", num_hosts, test_time, delay,
    #                      test_loop=num_tests, kind_gen="exp", first_run="no")
    # cmd = ". " + path + "/exp_alg1/copy_gen"
    # print(cmd)
    # os.system(cmd)
    #create_exp_run_file(path + "/exp_alg1")

    # Learning Algorithm
    delay = 10
    num_hosts = 5
    num_tests = 20
    test_time = 40
    create_generate_file(path + "/exp_alg3/double_syn", "/generator_file.txt", num_hosts, test_time, delay,
                         test_loop=num_tests, kind_gen="exp", first_run="yes")
    create_generate_file(path + "/exp_alg3/gready", "/generator_file.txt", num_hosts, test_time, delay,
                         test_loop=num_tests, kind_gen="exp", first_run="no")
    create_generate_file(path + "/exp_alg3/ucb", "/generator_file.txt", num_hosts, test_time, delay,
                         test_loop=num_tests, kind_gen="exp", first_run="no")
    create_generate_file(path + "/exp_alg3/t_sample", "/generator_file.txt", num_hosts, test_time, delay,
                         test_loop=num_tests, kind_gen="exp", first_run="no")
    create_generate_file(path + "/exp_alg3/internet", "/generator_file.txt", num_hosts, test_time, delay,
                         test_loop=num_tests, kind_gen="exp", first_run="no")
    create_generate_file(path + "/exp_alg3/cloud", "/generator_file.txt", num_hosts, test_time, delay,
                         test_loop=num_tests, kind_gen="exp", first_run="no")
    create_generate_file(path + "/exp_alg3/random", "/generator_file.txt", num_hosts, test_time, delay,
                         test_loop=num_tests, kind_gen="exp", first_run="no")
    cmd = ". " + path + "/exp_alg3/copy_gen"
    print(cmd)
    os.system(cmd)
    # create run files
    #create_exp_run_file(path + "/exp_alg3")
    create_folder_run_file(path)


create_generate_folder("/home/user/mininet/exp/same_delay_10ep_10host")
