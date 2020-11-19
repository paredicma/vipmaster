#-*- coding: utf-8 -*-
## Author               : Mustafa YAVUZ 
## E-mail               : msyavuz@gmail.com
## Version              : 1.0
## Date                 : 21.10.20120
## OS System            : Redhat/Centos 7
## DB Systems           : Postgresql, ( MySQL, Mongodb maybe in future )
## System Requirement   : python,mailx
from time import *
import os
import sys
import commands
from time import *
##################PARAMETERS##################
LOG_FILE="/var/log/vipmaster.log"
SILENT_MODE=False
RUN_FILE="/var/run/vipmaster.pid"
SLEEP_TIME=15
NETWORK_INT='team0'
NETWORK_NUMBER='0'
CLUSTER_NAME='CLUSTER_PG'
VIRTUAL_IP='10.10.10.10'
LOCALE_IP='localhost'
DB_TYPE='Postgresql'
DB_NAME='postgres'
DB_USER='vipservice'  ## superuser.
PASSWORDLESS_CONN=True
DB_PASSWORD='NoNeedBecauseOf_PWDLESSCONN'
DB_PORT='5432'
BIN_DIR='/usr/pgsql-12/bin/'
mailTO = 'TEAM-OPENDBA@turkcell.entp.tgc'
############################## GENERAL FUNCTION ###########################
def get_datetime():
	my_year=str(localtime()[0])
	my_mounth=str(localtime()[1])
	my_day=str(localtime()[2])
	my_hour=str(localtime()[3])
	my_min=str(localtime()[4])
	my_sec=str(localtime()[5])	
	if(len(str(my_mounth))==1):
		my_mounth="0"+my_mounth		
	if(len(my_day)==1):
		my_day="0"+my_day
	if(len(my_hour)==1):
		my_hour="0"+my_hour
	if(len(my_min)==1):
		my_min="0"+my_min
	if(len(my_sec)==1):
		my_sec="0"+my_sec
	return my_year+"."+my_mounth+"."+my_day+" "+my_hour+":"+my_min+":"+my_sec
def fileAppendWrite(file, writeText):
	try :
		fp=open(file,'ab')
		fp.write(writeText+'\n')
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
		fp.write(writeText+'\n')
		fp.close()
	except :
		print ('!!! An error is occurred while writing file !!!')
def logWrite(logFile,logText):
	if(SILENT_MODE):
		logText=get_datetime()+' ::: '+logText
		fileAppendWrite(logFile,logText)		
	else:
		print (logText)
		logText=get_datetime()+' ::: '+logText
		fileAppendWrite(logFile,logText)
############################## AUX FUNCTIONS ##################
def db_is_master():
	if( DB_TYPE=='Postgresql' ):
		if(PASSWORDLESS_CONN):
			getStatus,getResponse = commands.getstatusoutput(BIN_DIR+"psql -t -h "+LOCALE_IP+" -d "+DB_NAME+" -U "+DB_USER+" -p "+DB_PORT+" -c 'select pg_is_in_recovery()'")
			if ( getStatus==0 and getResponse.find('f')>-1 ):
				return True
			else:
				return False
		else:
			getStatus,getResponse = commands.getstatusoutput("export PGPASSWORD="+DB_PASSWORD+" ; "+ BIN_DIR+"psql -t -h "+LOCALE_IP+" -d "+DB_NAME+" -U "+DB_USER+" -p "+DB_PORT+" -c 'select pg_is_in_recovery()'")
			if ( getStatus==0 and getResponse.find('f')>-1 ):
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
	logWrite(LOG_FILE,"Arping command is processed.")
def ANNOUNCE_virtual_ip_isMine():
	process_return=os.system("/sbin/arping -c 1 -I "+NETWORK_INT+" -A -q "+VIRTUAL_IP)
	logWrite(LOG_FILE,"Announce VIP is mine!!!")
def UP_virtual_ip(): ## varsa 0 donerse basarili.
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
						sleep( SLEEP_TIME + SLEEP_TIME )
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
		pid=fileRead(RUN_FILE)[0].replace("\n","")
		logWrite(LOG_FILE,"vipservice is stopping. PID:"+str(pid))
		if(pid!=''):
			os.remove(RUN_FILE)
			os.system("kill "+pid)
		else:
			logWrite(LOG_FILE,"PID file is NOT found.")
	elif(param=='status'):
		if ( os.path.exists(RUN_FILE) ):
			pid=fileRead(RUN_FILE)[0].replace("\n","")
			getPidStatus,getPidResponse = commands.getstatusoutput("ps -ef | grep "+str(pid)+" | grep -v 'grep' | awk '{print $2}' ")
			if ( str(pid) == getPidResponse ):
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
