echo "***********************************"
echo "*** Start setting severs on EPS ***"
echo "***********************************"
sudo sshpass -p "123456" ssh -o stricthostkeychecking=no user@10.70.1.121 "source /home/user/run.csh" &
sudo sshpass -p "123456" ssh -o stricthostkeychecking=no user@10.70.1.123 "source /home/user/run.csh" &
sudo sshpass -p "123456" ssh -o stricthostkeychecking=no user@10.70.1.124 "source /home/user/run.csh" &
sudo sshpass -p "123456" ssh -o stricthostkeychecking=no user@10.70.1.125 "source /home/user/run.csh" &
#sudo sshpass -p "123456" ssh -o stricthostkeychecking=no user@10.70.1.126 "source /home/user/run.csh" &
#sudo sshpass -p "123456" ssh -o stricthostkeychecking=no user@10.70.1.127 "source /home/user/run.csh" &

echo "************************************"
echo "*** Finish setting servers on EPS***"
echo "************************************"