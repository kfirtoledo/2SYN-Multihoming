echo "***********************************"
echo "*** Start to clean algorithms   ***"
echo "***********************************"

sudo sshpass -p "123456" ssh user@10.70.1.120 "sudo bash /home/user/mininet/clean_gen.csh"
sudo sshpass -p "123456" ssh user@10.70.1.121 "sudo bash /home/user/mininet/clean_gen.csh"
sudo sshpass -p "123456" parallel-ssh -i -h ~/.pssh_hosts_files -t 10000 -A  sudo /home/user/mininet/exp/clean_gen.csh

echo "***********************************"
echo "*** Finish to clean algorithms  ***"
echo "***********************************"