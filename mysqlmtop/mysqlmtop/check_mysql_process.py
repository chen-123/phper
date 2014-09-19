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

def check_mysql_process(host,port,user,passwd,server_id,application_id,idc_type='ts'):
    try:
        datalist=[]
        connect=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=2,charset='utf8')
        cur=connect.cursor()
        connect.select_db('information_schema')
        processlist=cur.execute('select * from information_schema.processlist where Command !="Sleep" and DB !="information_schema";')
        if processlist: 
            for row in cur.fetchall():
		#print row
                for r in row:
                    datalist.append(r)
		#print datalist
            	result=datalist
            	#print result
            	sql="insert into mysql_process(server_id,application_id,pid,user,host,db,command,time,status,info,idc_type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                param=(server_id,application_id,result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7],idc_type)
                func.mysql_exec(sql,param)
		datalist = []
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

    func.mysql_exec("delete from mysql_process where idc_type='"+str(idc_type)+"'",'')

    servers=func.mysql_query("select id,host,port,application_id,status,idc_type from servers where idc_type='"+str(idc_type)+"' and is_delete=0;")
    if servers:
         print("%s: check_mysql_process controller started." % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),));
         plist = []
         for row in servers:
             server_id=row[0]
             host=row[1]
             port=row[2]
             application_id=row[3]
             status=row[4]
	     idc_type=row[5]
	     if host not in server_list:
                print "Deny host:"+str(host)
                continue

             if status <> 0:
                 p = Process(target = check_mysql_process, args = (host,port,user,passwd,server_id,application_id,idc_type))
                 plist.append(p)
                 p.start()

         for p in plist:
             p.join()
         print("%s: check_mysql_process controller finished." % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),))

if __name__=='__main__':
    main()
