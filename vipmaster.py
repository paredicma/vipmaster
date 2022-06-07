#-*- coding: utf-8 -*-
## Author               : Mustafa YAVUZ 
## E-mail               : msyavuz@gmail.com
## Version              : 1.2
## Date                 : 03.06.2022
## OS System            : Redhat/Centos/Rocky 7 and 8
## DB Systems           : Postgresql, MySQL, Mongodb, Oracle
## System Requirement   : python3, mailx
import os
import sys
import psutil
import subprocess
from time import *
from datetime import datetime
##################PARAMETERS##################
LOG_FILE="/var/log/vipmaster.log"
SILENT_MODE=False
RUN_FILE="/var/run/vipmaster.pid"
SLEEP_TIME=15
NETWORK_INT='ens18'
NETWORK_NUMBER='0'
CLUSTER_NAME='pgdb'
VIRTUAL_IP='10.10.10.11'
DB_TYPE='Postgresql'
BIN_DIR='/usr/pgsql-12/bin/'
DATA_DIR='/data/pgdata/12/'
mailTO = 'msyavuz@gmail.com'
############################## GENERAL FUNCTION ###########################
def fileAppendWrite(file, writeText):
	try :
		fp=open(file,'ab')
		fp.write(writeText.encode('utf-8')+'\n'.encode('utf-8'))
		fp.close()
	except :
		print ('!!! An error is occurred while writing file !!!')
def fileRead(file):
	returnTEXT=""
	try :
		fp=open(file,'r')
		returnTEXT=fp.readlines()
		fp.close()
		return returnTEXT
	except :
		print ('!!! An error is occurred while reading file !!!')
		return ""
def fileReadFull(file):
	returnTEXT=""
	try :
		fp=open(file,'r')
		returnTEXT=fp.read()
		fp.close()
		return returnTEXT
	except :
		print ('!!! An error is occurred while reading file !!!')
		return ""
def fileClearWrite(file, writeText):
	try :
		fp=open(file,'w')
		fp.write(writeText.encode('utf-8')+'\n'.encode('utf-8'))
		fp.close()
	except :
		print ('!!! An error is occurred while writing file !!!')
def logWrite(logFile,logText):
	if(SILENT_MODE):
		logText=str(datetime.now())+' ::: '+logText
		fileAppendWrite(logFile,logText)		
	else:
		print (logText)
		logText=str(datetime.now())+' ::: '+logText
		fileAppendWrite(logFile,logText)
############################## AUX FUNCTIONS ##################
def db_is_master():
	if( DB_TYPE=='Postgresql' ):
		recoveryState=subprocess.check_output([BIN_DIR+"pg_controldata", "-D", DATA_DIR])
		resultCode=str(recoveryState).find("in production")
		if(resultCode>0):
			return True
		else:
			return False
	elif( DB_TYPE=='Mysql' ):
		return False
	elif( DB_TYPE=='Mongodb' ):
		return False
	else:
		return False
def PING_virtual_ip(): ## OK -> return 0 , Not OK -> return 256
	ping_state=os.system('/bin/ping '+VIRTUAL_IP+' -c 4 > /dev/null')
	return ping_state
def HAS_virtual_ip(): ## OK -> return 0 , Not OK -> return 256 
      virtual_ip_state=os.system('/sbin/ifconfig | grep '+VIRTUAL_IP+' > /dev/null')
      return virtual_ip_state
def DOWN_virtual_ip():
	process_return=os.system("/sbin/ifconfig "+NETWORK_INT+":"+NETWORK_NUMBER+" down")
	logWrite(LOG_FILE,"VIP deactivated.")
def ANNOUNCE_virtual_ip_isMine():
	process_return=os.system("/sbin/arping -c 1 -I "+NETWORK_INT+" -A -q "+VIRTUAL_IP)
	logWrite(LOG_FILE,"Announce VIP is mine!!!")
def UP_virtual_ip(): ## .
	virtual_ip_state=os.system("/sbin/ifconfig "+NETWORK_INT+" add "+VIRTUAL_IP+"  > /dev/null")
	vip_state=int(virtual_ip_state)
	if (vip_state==0):
		logWrite(LOG_FILE,"VIP was designated!!!")
	else:
		logWrite(LOG_FILE,"Could NOT set VIP!!!")
	return vip_state
############################## AUX FUNCTIONS ##################	

##############################  DECISION PROCESS ##########################
def service_control(param): ## 
	if(param=='start'):
		logWrite(LOG_FILE,"vipservice started.")
		fileClearWrite(RUN_FILE,str(os.getpid()))
		while(1):
			if ( db_is_master() ) :
				if ( HAS_virtual_ip() != 0 ):   ## I do NOT have virtual IP
					if ( PING_virtual_ip() == 0 ): ## Virtual IP have been existed.
						sleep( SLEEP_TIME * 2 )
						if ( db_is_master() ) :
							UP_virtual_ip()
							ANNOUNCE_virtual_ip_isMine()
							if( SILENT_MODE==False ):
								os.system('nohup echo "'+CLUSTER_NAME+' New Primary DB -> '+str(os.uname()[1])+'" | mailx -s "'+CLUSTER_NAME+' Virtaul IP Owner Changed." '+mailTO+' &')
					else:
						UP_virtual_ip()
						ANNOUNCE_virtual_ip_isMine()
						if( SILENT_MODE==False ):
							os.system('nohup echo "'+CLUSTER_NAME+' New Primary DB -> '+str(os.uname()[1])+'" | mailx -s "'+CLUSTER_NAME+' Virtaul IP Owner Changed." '+mailTO+' &')					
			else:
				if ( HAS_virtual_ip() == 0 ):   ##I Have virtual IP
					DOWN_virtual_ip()
			sleep(SLEEP_TIME)
	elif(param=='stop'):
		DOWN_virtual_ip()
		pid=fileRead(RUN_FILE)[0].replace("\n","")
		logWrite(LOG_FILE,"vipservice is stopping. PID:"+str(pid))
		if(pid!=''):
			os.remove(RUN_FILE)
			os.system("kill "+pid)
		else:
			logWrite(LOG_FILE,"PID file is NOT found.")
	elif(param=='status'):
		if ( os.path.exists(RUN_FILE) ):
#			print (".vipmaster is running. Pid: "+str(pid))
			pid=fileRead(RUN_FILE)[0].replace("\n","")
			if psutil.pid_exists(int(pid)):
#			getPidStatus,getPidResponse = commands.getstatusoutput("ps -ef | grep "+str(pid)+" | grep -v 'grep' | awk '{print $2}' ")
#			if ( str(pid) == getPidResponse ):
				print (" vipmaster is running. Pid: "+str(pid))
			else:
				print (" vipmaster is NOT running.")
		else:
			print (" vipmaster is NOT running.") 
	else:
		logWrite(LOG_FILE,"WRONG PARAMETER :"+param+" (start|stop|status)")
def main():
	service_control(sys.argv[1])
main()
