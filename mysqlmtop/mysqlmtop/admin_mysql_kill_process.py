#!//bin/env python
#coding:utf-8
import os
import sys
import string
import time
import datetime
import MySQLdb
import global_functions as func
from multiprocessing import Process;


def admin_mysql_kill_process(host,port,user,passwd,pid,idc_type='ts'):
    datalist=[]
    try:
        connect=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=2,charset='utf8')
        cur=connect.cursor()
        #kill pid
        cur.execute("kill %s"%eval('pid'));
        print  "mysql pid %s been killed"%eval('pid')

    except MySQLdb.Error,e:
        pass
        print "Mysql Error %d: %s" %(e.args[0],e.args[1])


def main():
    #get idc type
    idc_type = func.get_config('idc','idc_type')

    if idc_type != "yf":
        print "ide_type error"
        return

    #get mysql servers list
    user = func.get_config('mysql_db','username')
    passwd = func.get_config('mysql_db','password')
    #get allow host
    server_list = func.get_config('mysql_db','allow_server_list')

    killed_pids=func.mysql_query("select p.pid,s.host,s.port,s.status,s.idc_type from mysql_process_killed p left join servers s on p.server_id=s.id where s.idc_type='"+str(idc_type)+"';")
    if killed_pids:
         print("%s: admin_mysql_kill_process controller started." % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),));
         plist = []
         for row in killed_pids:
	     print row
             pid=row[0]
             host=row[1]
             port=row[2]
	     status=row[3]
	     idc_type=row[4]
	     if host not in server_list:
                print "Deny host:"+str(host)
                continue

	     if status <> 0:
             	p = Process(target = admin_mysql_kill_process, args = (host,port,user,passwd,pid,idc_type))
             	plist.append(p)
             	p.start()

         for p in plist:
             p.join()
         print("%s: admin_mysql_kill_process controller finished." % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),))
         func.mysql_exec("delete from mysql_process_killed where idc_type='"+str(idc_type)+"'",'')


if __name__=='__main__':
    main()
