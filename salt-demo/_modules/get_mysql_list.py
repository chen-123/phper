#!/user/bin/env python

import os
import sys
import socket
import commands

def get_mysql_list():
	"""
	get mysql list from shell 
	CLI Example:
	    salt '*' get_mysql_list.get_mysql_list
	"""
	list_str=commands.getoutput("ps aux|grep mysql|grep 'socket'|grep -v 'mysql.sock'|sed 's/ /#/g'|awk '{print $0}'")
	if( not len(list_str)):
                return []
	list=list_str.split("\n")
	result=[]
	for line in list:
		tmp=line.split("#")
		dict_tmp={}
		for m in tmp:
			if m.startswith('--'):
				tmp_conf=m.split("=")
				if(len(tmp_conf[0][2:])<20 and len(tmp_conf)>1):
					dict_tmp[tmp_conf[0][2:]]=tmp_conf[1]
		mysql_conn_status,mysql_str=commands.getstatusoutput("/opt/phpdba/mysql/bin/mysql -S "+str(dict_tmp['socket'])+" -p'hanfuboyuan0619' -e 'select version();'|grep -v version")
		if(mysql_conn_status):
			mysql_conn_status,mysql_str=commands.getstatusoutput("/opt/phpdba/mysql/bin/mysql -S "+str(dict_tmp['socket'])+" -p'ts@)!@fuyuanci' -e 'select version();'|grep -v version")

		if( not mysql_conn_status ):
			dict_tmp['version'] = mysql_str
		else:
			dict_tmp['version'] = "null"

		database_status,database_str=commands.getstatusoutput("/opt/phpdba/mysql/bin/mysql -S "+str(dict_tmp['socket'])+" -p'hanfuboyuan0619' -e 'show databases;'|grep -v -E 'Database|information_schema|mysql'")
		if(database_status):
			database_status,database_str=commands.getstatusoutput("/opt/phpdba/mysql/bin/mysql -S "+str(dict_tmp['socket'])+" -p'ts@)!@fuyuanci' -e 'show databases;'|grep -v -E 'Database|information_schema|mysql'")

		if( not database_status):
			dict_tmp['database'] = database_str.replace("\n",',')
		else:
			dict_tmp['database'] = "null"

		result.append(dict_tmp)
	return result
			
def get_mysql_list_sql():
	"""
	get mysql list insert sql 
	CLI Example:
	    salt '*' get_mysql_list.get_mysql_list_sql
	"""
	list = get_mysql_list()
	host_ip = commands.getoutput("ifconfig | awk -F'addr:|Bcast' '/Bcast/{print $2}'|grep -v '192.168'|head -n 1").strip()
	list_sql=[]
	option_list=['socket','database','log-error','basedir','defaults-file','datadir','user','pid-file','port']
	for instance in list:
		for option in option_list:
			if( not instance.has_key(option)):
				instance[option]="null"
		insert_sql="insert into `mysql_instance` (`socket`,`database`,`log-error`,`basedir`,`defaults-file`,`datadir`,`version`,`thread_user`,`pid-file`,`port`,`host`) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (instance['socket'],instance['database'],instance['log-error'],instance['basedir'],instance['defaults-file'],instance['datadir'],instance['version'],instance['user'],instance['pid-file'],instance['port'],host_ip)
		list_sql.append(insert_sql)
	return list_sql

def grant_mysql_user(sql="select version();"):
        """
        get mysql list from shell
        CLI Example:
            salt '*' get_mysql_list.grant_mysql_user
        """
        list_str=commands.getoutput("ps aux|grep mysql|grep 'socket'|grep -v 'mysql.sock'|sed 's/ /#/g'|awk '{print $0}'")
        if( not len(list_str)):
                return []
        list=list_str.split("\n")
        result=[]
        host_ip = commands.getoutput("ifconfig | awk -F'addr:|Bcast' '/Bcast/{print $2}'|grep -v '192.168'|head -n 1").strip()
        for line in list:
                tmp=line.split("#")
                dict_tmp={}
                ret={}
                for m in tmp:
                        if m.startswith('--'):
                                tmp_conf=m.split("=")
                                if(len(tmp_conf[0][2:])<20 and len(tmp_conf)>1):
                                        dict_tmp[tmp_conf[0][2:]]=tmp_conf[1]
                if(os.path.isfile('/opt/phpdba/mysql/bin/mysql')):
                        mysql_ret_status,mysql_ret=commands.getstatusoutput("/opt/phpdba/mysql/bin/mysql -S "+str(dict_tmp['socket'])+" -p'hanfuboyuan0619' -e '"+str(sql)+"'")
                        if(mysql_ret_status):
                                mysql_ret_status,mysql_ret=commands.getstatusoutput("/opt/phpdba/mysql/bin/mysql -S "+str(dict_tmp['socket'])+" -p'ts@)!@fuyuanci' -e '"+str(sql)+"'")

                        ret['host'] = host_ip
                        ret['sql'] = sql
                        ret['ret_status'] = mysql_ret_status
                        ret['ret'] = mysql_ret
                result.append(ret)
        return result
