for pid in $(ps aux | grep "gener" | awk '{print $2}'); do kill -9 $pid;done
for pid in $(ps aux | grep "iperf" | awk '{print $2}'); do kill -9 $pid;done