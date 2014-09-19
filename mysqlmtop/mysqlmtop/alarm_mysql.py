#!/bin/env python
#-*-coding:utf-8-*-
#import time
#import datetime
from datetime import *
import global_functions as func


def get_alarm_mysql_status(idc_type='ts'):
    sql="select a.application_id,a.server_id,a.create_time,a.connect,a.connections,a.active,b.send_mail,b.alarm_connections,b.alarm_active,b.threshold_connections,b.threshold_active from mysql_status a, servers b where a.server_id=b.id and b.idc_type='"+str(idc_type)+"';"
    result=func.mysql_query(sql)
    if result <> 0:
        for line in result:
            application_id=line[0]
            server_id=line[1]
            create_time=line[2]
            connect=line[3]
            connections=line[4]
            active=line[5]
            send_mail=line[6]
            alarm_connections=line[7]
            alarm_active=line[8]
            threshold_connections=line[9]
            threshold_active=line[10]

            if connect <> "success":
                    sql="insert into alarm(application_id,server_id,create_time,db_type,alarm_type,alarm_value,level,message,send_mail,idc_type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                    param=(application_id,server_id,create_time,'mysql','connect',connect,'error','数据库连接失败',send_mail,idc_type)    
                    func.mysql_exec(sql,param)
            else:
                if int(alarm_connections)==1:
                    if int(connections)>=int(threshold_connections):
                        sql="insert into alarm(application_id,server_id,create_time,db_type,alarm_type,alarm_value,level,message,send_mail,idc_type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                        param=(application_id,server_id,create_time,'mysql','connections',connections,'warning','数据库总连接数过多',send_mail,idc_type)                 
                        func.mysql_exec(sql,param)
                if int(alarm_active)==1:
                    if int(active)>=int(threshold_active):
                        sql="insert into alarm(application_id,server_id,create_time,db_type,alarm_type,alarm_value,level,message,send_mail,idc_type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                        param=(application_id,server_id,create_time,'mysql','active',active,'warning','数据库活动连接过多',send_mail,idc_type)
                        func.mysql_exec(sql,param)
    else:
       pass


def get_alarm_mysql_replcation(idc_type='ts'):
    sql="select a.application_id,a.server_id,a.create_time,a.slave_io_run,a.slave_sql_run,a.delay,b.send_mail,b.alarm_repl_status,b.alarm_repl_delay,b.threshold_repl_delay from mysql_replication a,servers b  where a.server_id=b.id and a.is_slave='1' and b.idc_type='"+str(idc_type)+"';"
    result=func.mysql_query(sql)
    if result <> 0:
        for line in result:
            application=line[0]
            server_id=line[1]
            create_time=line[2]
            slave_io_run=line[3]
            slave_sql_run=line[4]
            delay=line[5]
            send_mail=line[6]
            alarm_repl_status=line[7]
            alarm_repl_delay=line[8]
            threshold_repl_delay=line[9]
            if alarm_repl_status==1:
                if (slave_io_run== "Yes") and (slave_sql_run== "Yes"):
                    if alarm_repl_delay=="yes":
                        if int(delay)>=int(threshold_repl_delay):
                            sql="insert into alarm(application_id,server_id,create_time,db_type,alarm_type,alarm_value,level,message,send_mail,idc_type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                            param=(application,server_id,create_time,'mysql','delay',delay,'warning','数据库备库延时',send_mail,idc_type)
                            func.mysql_exec(sql,param)
		else:
                    sql="insert into alarm(application_id,server_id,create_time,db_type,alarm_type,alarm_value,level,message,send_mail,idc_type) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                    param=(application,server_id,create_time,'mysql','replication','IO Thread:'+slave_io_run+',SQL Thread:'+slave_sql_run,'error','数据库同步进程停止',send_mail,idc_type)
                    func.mysql_exec(sql,param)
    else:
       pass


def send_alarm_mail(idc_type='ts'):
    sql="select alarm.application_id,app.display_name application,alarm.server_id,servers.host,servers.port,alarm.create_time,db_type,alarm_type,alarm_value,level,message,alarm.send_mail,servers.alarm_time,servers.threshold_starttime,servers.threshold_endtime from alarm left join servers on alarm.server_id=servers.id left join application app on servers.application_id=app.id where servers.idc_type='"+str(idc_type)+"';"
    result=func.mysql_query(sql)
    if result <> 0:
        send_alarm_mail = func.get_option('send_alarm_mail')
        mail_to_list = func.get_option('mail_to_list')
        mailto_list=mail_to_list.split(';')
	global_alarm_type=func.get_config('global_alarm_type','alarm_type')
        global_alarm_type_list=global_alarm_type.split(',')
        for line in result:
            application_id=line[0]
            application=line[1]
            server_id=line[2]
            host=line[3]
            port=line[4]
            create_time=line[5]
            db_type=line[6]
            alarm_type=line[7]
            alarm_value=line[8]
            level=line[9]
            message=line[10]
            send_mail=line[11]
	    alarm_time=line[12]
	    threshold_starttime=line[13]
	    threshold_endtime=line[14]
	    app_email=func.get_application_alarm_email(str(application_id))
            app_email_list=app_email.split(',')
            for email_app in app_email_list:
                if email_app not in mailto_list:
                        mailto_list.append(email_app)
                else:
                        pass


            if send_alarm_mail=="1":
                if send_mail==1:
                    mail_subject=message+' 当前值:'+alarm_value+' 服务器:'+application+'-'+host+':'+port+' 时间:'+create_time.strftime('%Y-%m-%d %H:%M:%S')
                    mail_content="请检查下!"
		    now_hour = ("0"+str(datetime.now().hour) if datetime.now().hour<10 else str(datetime.now().hour))+":"+( "0"+str(datetime.now().minute) if datetime.now().minute<10  else str(datetime.now().minute))
		    if alarm_type not in global_alarm_type_list:
		    	if (int(alarm_time) == 1) and (threshold_starttime.strip() != "") and (threshold_endtime.strip() != "") and (threshold_endtime > threshold_starttime) and (now_hour <= threshold_endtime) and (now_hour >= threshold_starttime):
                    		result_mail = func.send_mail(mailto_list,mail_subject,mail_content)
		    	elif int(alarm_time) != 1:
				result_mail = func.send_mail(mailto_list,mail_subject,mail_content)
		    	else:
				result_mail = False
		    else:
			result_mail = func.send_mail(mailto_list,mail_subject,mail_content)

                    if result_mail:
                        send_mail_status=1
                    else:
                        send_mail_status=0
                else:
                    send_mail_status=0
            else:
                send_mail_status=0


            if send_mail_status==1:
                func.mysql_exec("insert into alarm_history(application_id,server_id,create_time,db_type,alarm_type,alarm_value,level,message,send_mail,send_mail_status,idc_type) select application_id,server_id,create_time,db_type,alarm_type,alarm_value,level,message,send_mail,1,'"+str(idc_type)+"' from alarm;",'')
            elif send_mail_status==0:
                func.mysql_exec("insert into alarm_history(application_id,server_id,create_time,db_type,alarm_type,alarm_value,level,message,send_mail,send_mail_status,idc_type) select application_id,server_id,create_time,db_type,alarm_type,alarm_value,level,message,send_mail,0,'"+str(idc_type)+"' from alarm;",'')
            func.mysql_exec("delete from alarm where idc_type='"+str(idc_type)+"'",'')

    else:
        pass


if __name__ == '__main__':
    #get idc type
    #print("%s: alarm_mysql controller started." % (datetime.time.strftime('%Y-%m-%d %H:%M:%S', datetime.time.localtime()),));
    idc_type = func.get_config('idc','idc_type')
    get_alarm_mysql_status(idc_type)
    get_alarm_mysql_replcation(idc_type)
    send_alarm_mail(idc_type)
    #print("%s: alarm_mysql controller finished." % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),))














