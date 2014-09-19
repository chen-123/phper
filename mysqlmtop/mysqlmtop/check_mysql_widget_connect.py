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

def check_mysql_widget(host,port,user,passwd,server_id,idc_type='ts'):
    try:
        connect=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=2,charset='utf8')
        cur=connect.cursor()
        connect.select_db('information_schema')
        totalresult=cur.execute("select SUBSTRING_INDEX(host,':',1) as connect_server, user connect_user,db connect_db, count(SUBSTRING_INDEX(host,':',1)) as connect_count  from information_schema.processlist where db is not null and db!='information_schema' and db !='performance_schema' group by connect_server ;");
        if totalresult:
            for row in cur.fetchall():
                datalist=[]
                for r in row:
                    datalist.append(r)
                result=datalist
                if result:
                    connect_server=result[0]
                    connect_user=result[1]
                    connect_db=result[2]
                    connect_count=result[3]
                    sql="insert into mysql_widget_connect(server_id,connect_server,connect_user,connect_db,connect_count,idc_type) values(%s,%s,%s,%s,%s,%s);"
                    param =(server_id,connect_server,connect_user,connect_db,connect_count,idc_type)
                    func.mysql_exec(sql,param)        

        cur.close()
        connect.close()
        exit

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

    #func.mysql_exec("truncate table mysql_widget_connect",'')
    func.mysql_exec("delete from mysql_widget_connect where idc_type='"+str(idc_type)+"'",'')
	
    servers=func.mysql_query("select id,host,port,status,idc_type from servers where idc_type='"+str(idc_type)+"' and is_delete=0;")
    if servers:
        print("%s: check_mysql_widget_connect controller started." % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),));
        plist = []
        for row in servers:
            server_id=row[0]
            host=row[1]
            port=row[2]
	    status=row[3]
	    idc_type=row[4]
            if host not in server_list:
                print "Deny host:"+str(host)
                continue

            if status <> 0:
            	p = Process(target = check_mysql_widget, args = (host,port,user,passwd,server_id,idc_type))
            	plist.append(p)
            	p.start()

        for p in plist:
            p.join()
        print("%s: check_mysql_widget_connect controller finished." % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),))
                     

if __name__=='__main__':
    main()
