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

def check_mysql_replication(host,port,user,passwd,server_id,application_id,idc_type='ts'):
    try:
        connect=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=2,charset='utf8')
        cur=connect.cursor()
        connect.select_db('information_schema')
        master_thread=cur.execute("select * from information_schema.processlist where COMMAND = 'Binlog Dump'or COMMAND = 'Binlog Dump GTID';")
        slave_status=cur.execute('show slave status;')
	print str(server_id)+"=>"+host+":"+port
      
        datalist=[]
        if master_thread >= 1:
            datalist.append(int(1))
            if slave_status <> 0:
                datalist.append(int(1))
            else:
                datalist.append(int(0))
        else:
            datalist.append(int(0))
            if slave_status <> 0:
		if server_id in [2,45]:
                	datalist.append(int(0))
		else:
			datalist.append(int(1))
            else:
                datalist.append(int(0))
        
	if server_id in [2]:
		slave_status = 0  

	 
        if slave_status <> 0:
            read_only=cur.execute("select * from information_schema.global_variables where variable_name='read_only';")
            result=cur.fetchone()
            datalist.append(result[1])
            slave_info=cur.execute('show slave status;')
            result=cur.fetchone()
            master_server=result[1]
            master_port=result[3]
            slave_io_run=result[10]
            slave_sql_run=result[11]
            delay=result[32]
            current_binlog_file=result[9]
            current_binlog_pos=result[21]
            master_binlog_file=result[5]
            master_binlog_pos=result[6]
     
            datalist.append(master_server)
            datalist.append(master_port)
            datalist.append(slave_io_run)
            datalist.append(slave_sql_run)
            datalist.append(delay)
            datalist.append(current_binlog_file)
            datalist.append(current_binlog_pos)
            datalist.append(master_binlog_file)
            datalist.append(master_binlog_pos)

        elif master_thread >= 1:
            read_only=cur.execute("select * from information_schema.global_variables where variable_name='read_only';")
            result=cur.fetchone()
            datalist.append(result[1])
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            datalist.append('---')
            master=cur.execute('show master status;')
            master_result=cur.fetchone()
            datalist.append(master_result[0])
            datalist.append(master_result[1])

        else:
            datalist=[]
            
        cur.close()
        connect.close()
        result=datalist
        if result:
            sql="insert into mysql_replication(server_id,application_id,is_master,is_slave,read_only,master_server,master_port,slave_io_run,slave_sql_run,delay,current_binlog_file,current_binlog_pos,master_binlog_file,master_binlog_pos,idc_type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            param=(server_id,application_id,result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7],result[8],result[9],result[10],result[11],idc_type)
            func.mysql_exec(sql,param)
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

    func.mysql_exec("insert into mysql_replication_history(idc_type,server_id,application_id,is_master,is_slave,read_only,master_server,master_port,slave_io_run,slave_sql_run,delay,current_binlog_file,current_binlog_pos,master_binlog_file,master_binlog_pos,create_time,YmdHi) select '"+str(idc_type)+"',server_id,application_id,is_master,is_slave,read_only,master_server,master_port,slave_io_run,slave_sql_run,delay,current_binlog_file,current_binlog_pos,master_binlog_file,master_binlog_pos,create_time, LEFT(REPLACE(REPLACE(REPLACE(create_time,'-',''),' ',''),':',''),12) from mysql_replication where idc_type='"+str(idc_type)+"';",'')
    func.mysql_exec("delete from  mysql_replication where idc_type='"+str(idc_type)+"'",'')


    servers=func.mysql_query("select id,host,port,application_id,status,idc_type from servers where idc_type='"+str(idc_type)+"' and is_delete=0;")
    if servers:
        print("%s: check_mysql_replication controller started." % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),));
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
                p = Process(target = check_mysql_replication, args = (host,port,user,passwd,server_id,application_id,idc_type))
                plist.append(p)
                p.start()

        for p in plist:
            p.join()
        print("%s: check_mysql_replication controller finished." % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),))


if __name__=='__main__':
    main()
