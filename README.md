# vipmaster
VIPMASTER (VIP Management service for Master-Slave DB Cluster) SETUP 

Supported Linux Version : Centos/RHEL 7 and 8
Python version: 3

Download vipmaster.py and vipmaster.service

FOR ALL CLUSTER SERVERS

root # mkdir /opt/vipmaster/

root # cp vipmaster.py /opt/vipmaster/

root # cp vipmaster.service /usr/lib/systemd/system/

root # systemctl daemon-reload


configure vipmaster.py according to your network interface and VIP address

root # vi /opt/vipmaster/vipmaster.py


start service

root# systemctl enable vipmaster.service

root# systemctl start vipmaster.service

