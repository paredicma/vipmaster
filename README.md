# vipmaster
VIPMASTER (VIP Management service for Master-Slave DB Cluster) SETUP 

Supported Linux Version : Centos/RHEL 7 and 8

Download vipmaster.py and vipmaster.service

FOR ALL CLUSTER SERVERS

root # mkdir /opt/vipmaster/

root # cp vipmaster.py /opt/vipmaster/

root # cp vipmaster.service /usr/lib/systemd/system/

root # systemctl daemon-reload


for postgresql

psql #  create user vipservice encrypted password 'secretpass';

psql #  grant pg_monitor to vipservice ;


configure vipmaster.py

root # vi /opt/vipmaster/vipmaster.py


start service

root# systemctl enable vipmaster.service

root# systemctl start vipmaster.service

