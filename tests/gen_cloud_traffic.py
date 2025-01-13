import os
import  numpy as np
from datetime import date
from datetime import datetime
today = date.today()
now = datetime.now()

dest2_google_IP= "35.213.185.161"
dest1_google_IP   = "35.214.110.27"

dest2_aws_IP   = "54.179.218.212"
dest1_aws_IP      = "35.179.81.171"

dest2_azure_IP   = "104.215.253.99"
dest1_azure_IP      = "51.104.197.37"

def create_cloud_flow_check(dest,delay,num_checks,clouds,path):
   hour = int(now.strftime("%H"))
   minute = int(now.strftime("%M"))
   for idx,cl in enumerate(clouds):
      folder_path=path +cl+"/"
      if not os.path.exists(folder_path):
         os.makedirs(folder_path)
      if cl == "internet" : dest_ip = dest
      elif cl == "aws"    : dest_ip = dest1_aws_IP
      elif cl == "azure"  : dest_ip = dest1_azure_IP
      else                : dest_ip = dest1_google_IP

      f_name = folder_path + "cloud_check.csh"
      f = open(f_name, "w+")
      dest_port = 5001+idx
      for i in range(num_checks):
         f.write("echo \"start check {} using {} \" \n".format(str(i),cl ))
         hour_i= (hour + int((delay/(60*60)) *i)) % 24
         minute_i = (minute + delay/60 * i) % 60
         f.write("sudo iperf3 -p {} -c {} --omit 3 -J --logfile {}test_{}_time_{}_{}.txt \n".format(dest_port,dest_ip,folder_path, str(i), hour_i, minute_i))
         f.write("sudo sleep " + str(delay) + "\n")
      f.close
def create_run_file(clouds,path):
   f_name =  path+ "/run_all.csh"
   f = open(f_name, "w+")
   for idx,cl in enumerate(clouds):
      run_file= path +cl+"/cloud_check.csh"
      f.write("source  {} &\n".format(run_file))
      f.write("sudo sleep 30 \n")
   f.close

if __name__ == "__main__":
   # dd/mm/YY
   d1 = today.strftime("%d_%m_%Y")
   dest= dest2_google_IP
   delay=60* 20
   num_checks= 24 *3
   clouds=["internet","aws","azure"]

   path= "/home/user/cloud/exp/dest2_"+d1 +"/"
   create_cloud_flow_check(dest,delay,num_checks,clouds,path)
   create_run_file(clouds, path)

