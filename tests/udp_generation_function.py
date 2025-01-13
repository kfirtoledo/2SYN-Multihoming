

def th_one_cloud_shutdown(f,test_loop,j ,duration, type_test,kind_gen,sleep_val,sleep_arr,aws):

    # for cuting off the throughput
    if (j == int(test_loop / 4)):
        if (not aws):
            #f.write("sudo tc qdisc del dev ens1 root handle 1: tbf rate 300mbit burst 256kbit  limit 300mbit \n")
            f.write("sudo tc qdisc add dev ens1 parent 1: handle 2: tbf rate 100mbit  burst 256kbit  limit 100mbit   \n")
        else:
            f.write("sudo tc qdisc add dev ens1 parent 1: handle 2: tbf rate 100mbit  burst 256kbit  limit 100mbit   \n")
    elif (j == int((test_loop / 4)*3)):
        if (not aws):
            f.write("sudo tc qdisc del dev ens1 parent 1: handle 2: tbf rate 100mbit  burst 256kbit  limit 100mbit \n" )
            f.write("sudo tc qdisc del dev ens1 root handle 1: netem delay 20ms \n")
            f.write("sudo tc qdisc add dev ens1 root handle 1: netem delay 20ms \n")
           #f.write("sudo tc qdisc add dev ens1 root handle 1: tbf rate 300mbit burst 256kbit  limit 300mbit \n")
        else:
            f.write("sudo tc qdisc del dev ens1 parent 1: handle 2: tbf rate 100mbit  burst 256kbit  limit 100mbit \n" )
            f.write("sudo tc qdisc del dev ens1 root handle 1: netem delay 1ms  \n")
            f.write("sudo tc qdisc add dev ens1 root handle 1: netem delay 1ms  \n")
    else:
        if (j < test_loop / 4) or j > (test_loop / 4 * 3):
            duration= round(duration / 5) if type_test == "data" else duration
            f.write("sudo sleep " + str(duration) + "\n")
        else:
            duration= round(duration ) if type_test == "data" else duration
            f.write("sudo sleep " + str(int(duration/5)) + "\n")
    if (sleep_val > 0):
        if kind_gen == "exp":
            sleep_time = sleep_arr[j]
        else:
            sleep_time = sleep_val
        f.write("sudo sleep " + str(sleep_time) + "\n")

def th_one_time_shutdown(f,test_loop,j ,duration, type_test,kind_gen,sleep_val,sleep_arr,aws):

    # for cuting off the throughput
    if (j == int(test_loop / 4)):
        if (not aws):
            f.write("sudo tc qdisc del dev ens1 root handle 1: tbf rate 300mbit burst 256kbit  limit 300mbit \n")
            f.write("sudo tc qdisc add dev ens1 root handle 1: tbf rate 10mbit  burst 256kbit  limit 10mbit   \n")
        else:
            f.write(
                "sudo tc qdisc add dev ens1 parent 1: handle 2: tbf rate 10mbit  burst 64kbit  limit 10mbit   \n")
    elif (j == int(test_loop / 2)):
        if (not aws):
            f.write("sudo tc qdisc del dev ens1 root handle 1: tbf rate 10mbit  burst 256kbit  limit 10mbit \n" )
            f.write("sudo tc qdisc add dev ens1 root handle 1: tbf rate 300mbit burst 256kbit  limit 300mbit \n")
        else:
            f.write("sudo tc qdisc del dev ens1 parent 1: handle 2: tbf rate 10mbit  burst 64kbit  limit 10mbit\n")
            f.write("sudo tc qdisc del dev ens1 root handle 1: netem delay 1ms  \n")
            f.write("sudo tc qdisc add dev ens1 root handle 1: netem delay 1ms  \n")
            f.write("sudo tc qdisc add dev ens2f0 parent 1: handle 2: tbf rate 10mbit  burst 64kbit  limit 10mbit\n")
    elif (j == int((test_loop / 4 ) *3)):
        if (not aws):
            f.write("sudo tc qdisc del dev ens2f0 parent 1: handle 2: tbf rate 10mbit  burst 64kbit  limit 10mbit\n")
            f.write("sudo tc qdisc del dev ens2f0 root handle 1: netem delay 1ms  \n")
            f.write("sudo tc qdisc add dev ens2f0 root handle 1: netem delay 1ms  \n")
    else:
        if (j < test_loop / 4) or j > (test_loop / 4 * 3):
            duration= round(duration / 10) if type_test == "data" else duration
            f.write("sudo sleep " + str(duration) + "\n")
        else:
            duration= round(duration / 5) if type_test == "data" else duration
            f.write("sudo sleep " + str(duration) + "\n")
    if (sleep_val > 0):
        if kind_gen == "exp":
            sleep_time = sleep_arr[j]
        else:
            sleep_time = sleep_val
        f.write("sudo sleep " + str(sleep_time) + "\n")

def th_multiple_time_shutdown(f, test_loop, j, duration, type_test, kind_gen, sleep_val, sleep_arr, aws,freq,sleep_if):
    # for cuting off the throughput
    #print("test_loop {} freq {},{},  test_loop % freq {}".format(test_loop,freq,j, test_loop % freq))

    if ( int((j % freq) == 0) and  int((j %(2*freq)) != 0)):
        sleep_if = "CLOUD"
        if (not aws):
            f.write("sudo tc qdisc del dev ens1 root handle 1: tbf rate 300mbit burst 256kbit  limit 300mbit \n")
            f.write("sudo tc qdisc add dev ens1 root handle 1: tbf rate 10mbit  burst 256kbit  limit 10mbit   \n")
            f.write("sudo tc qdisc del dev ens2f0 root handle 1: tbf rate 10mbit  burst 256kbit  limit 10mbit\n")
            f.write("sudo tc qdisc add dev ens2f0 root handle 1: tbf rate 100mbit  burst 256kbit  limit 100mbit\n")

        else:
            f.write(
                "sudo tc qdisc add dev ens1 parent 1: handle 2: tbf rate 10mbit  burst 64kbit  limit 10mbit   \n")

    elif (int(j % (2*freq) == 0) and j != 0):
        sleep_if = "INTERNET"
        if (not aws):
            f.write("sudo tc qdisc del dev ens1 root handle 1: tbf rate 10mbit  burst 256kbit  limit 10mbit \n")
            f.write("sudo tc qdisc add dev ens1 root handle 1: tbf rate 300mbit burst 256kbit  limit 300mbit \n")
            f.write("sudo tc qdisc del dev ens2f0 root handle 1:  tbf rate 100mbit  burst 256kbit  limit 100mbit\n")
            f.write("sudo tc qdisc add dev ens2f0 root handle 1: tbf rate 10mbit  burst 256kbit  limit 10mbit \n")

        else:
            f.write("sudo tc qdisc del dev ens1 parent 1: handle 2: tbf rate 10mbit  burst 64kbit  limit 10mbit\n")
            f.write(
                "sudo tc qdisc add dev ens2f0 parent 1: handle 2: tbf rate 10mbit  burst 64kbit  limit 10mbit\n")
    else:
        # if (j < test_loop / 4) or j > (test_loop / 4 * 3):
        #     duration = round(duration / 10) if type_test == "data" else duration
        #     f.write("sudo sleep " + str(duration) + "\n")
        # else:
        duration = round(duration / 5) if type_test == "data" else duration
        if (sleep_if == "CLOUD"):
            duration= duration * 2
            duration = duration if duration > 40 else 40
        f.write("sudo sleep " + str(duration) + "\n")
    if (int(j) == test_loop-1):
        if (not aws):
            f.write("sudo tc qdisc del dev ens1 root handle 1: tbf rate 10mbit  burst 256kbit  limit 10mbit   \n")
            f.write("sudo tc qdisc add dev ens1 root handle 1: tbf rate 300mbit burst 256kbit  limit 300mbit \n")
            f.write("sudo tc qdisc del dev ens2f0 root handle 1: tbf rate 10mbit  burst 256kbit  limit 10mbit\n")
            f.write("sudo tc qdisc add dev ens2f0 root handle 1: tbf rate 100mbit  burst 256kbit  limit 100mbit\n")

    if (sleep_val > 0):
        if kind_gen == "exp":
            sleep_time = sleep_arr[j]
        else:
            sleep_time = sleep_val
        f.write("sudo sleep " + str(sleep_time) + "\n")
    return sleep_if
def th_shutdown(f,test_loop,j ,duration, type_test,kind_gen,sleep_val,sleep_arr,aws,bw_limit,type_shutdown):

    # for cuting off the throughput
    IF_Shutdown = "ens1" if type_shutdown == "CLOUD_SHUTDOWN" else "ens2f0"
    TH_val      = "300mbit" if type_shutdown == "CLOUD_SHUTDOWN" else "100mbit"
    th_drop= "10"#"50"
    if (j == 0):
        if (not aws):
            f.write("sudo tc qdisc del dev ens1 parent 1: handle 2: tbf rate "+th_drop+"mbit  burst 256kbit  limit "+th_drop+"mbit   \n")
            f.write("sudo tc qdisc del dev "  + IF_Shutdown +" root handle 1: netem delay 20ms  \n")
            f.write("sudo tc qdisc add dev " + IF_Shutdown +  " root handle 1: tbf rate 300mbit burst 256kbit  limit 300mbit \n")
            f.write("sudo tc qdisc add dev "  + IF_Shutdown +" root handle 1: netem delay 20ms  \n")
        else:
            f.write("sudo tc qdisc del dev "  + IF_Shutdown +" parent 1: handle 2: tbf rate "+th_drop+"mbit  burst 256kbit  limit "+th_drop+"mbit\n")
            f.write("sudo tc qdisc del dev "  + IF_Shutdown +" root handle 1: netem delay 1ms  \n")
            f.write("sudo tc qdisc add dev " + IF_Shutdown + " root handle 1: netem delay 1ms  \n")
            f.write("sudo tc qdisc add dev " + IF_Shutdown + " parent 1: handle 2: tbf rate 300mbit  burst 256kbit  limit 300mbit\n")


    elif (j == int(test_loop * (0.4))):
        if (not aws):
            f.write("sudo tc qdisc del dev " + IF_Shutdown + " parent 1: handle 2: tbf rate 300mbit  burst 256kbit  limit 300mbit\n")
            f.write("sudo tc qdisc add dev "  + IF_Shutdown +" parent 1: handle 2: tbf rate "+th_drop+"mbit  burst 256kbit  limit "+th_drop+"mbit   \n")
        else:
            f.write("sudo tc qdisc add dev "  + IF_Shutdown +" parent 1: handle 2: tbf rate "+th_drop+"mbit  burst 256kbit  limit "+th_drop+"mbit   \n")
    else:
            sleep_duration= round(duration / (bw_limit/8)) if type_test == "data" else duration
            f.write("sudo sleep " + str(sleep_duration) + "\n")

    if (sleep_val > 0):
        if kind_gen == "exp":
            sleep_time = sleep_arr[j]
        else:
            sleep_time = sleep_val
        f.write("sudo sleep " + str(sleep_time) + "\n")