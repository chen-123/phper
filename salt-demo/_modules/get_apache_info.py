#!/user/bin/env python

import os
import sys
import socket
import commands

def get_apache_vhostlist():
        """
        get apache VirtualHost from shell
        CLI Example:
            salt '*' get_apache_info.get_apache_vhostlist
        """
        apache_num=commands.getoutput("ps -e |grep http|grep -v grep|grep -v cacti_httpd|wc -l")
        if( not apache_num):
                return []
        result = []
	list = []
	#host_ip = commands.getoutput("ifconfig | awk -F'addr:|Bcast' '/Bcast/{print $2}'|grep -v '192.168'|head -n 1").strip()
	if(os.path.isfile('/opt/ci123/apache/bin/apachectl')):
        	apache_ret_status,apache_ret=commands.getstatusoutput("/opt/ci123/apache/bin/apachectl -t -D DUMP_VHOSTS")
		if(not apache_ret_status):
			list=apache_ret.split("\n")
	for line in list:
		#tmp = line.strip()
		tmp = line
		if(tmp.find('a NameVirtualHost') != -1):
			result.append(tmp)
			port=tmp.split("is")[0].strip()
		if(tmp.find('httpd.conf') != -1):
			result.append(tmp)
        return result
def get_apache_infolist(arg="-V"):
        """
        get apache infolist from shell
        CLI Example:
            salt '*' get_apache_info.get_apache_infolist
        """
        apache_num=commands.getoutput("ps -e |grep apache|grep -v grep|wc -l")
        if( not apache_num):
                return []
        result = []
        list = []
        #host_ip = commands.getoutput("ifconfig | awk -F'addr:|Bcast' '/Bcast/{print $2}'|grep -v '192.168'|head -n 1").strip()
        if(os.path.isfile('/opt/ci123/apache/bin/apachectl')):
                apache_ret_status,apache_ret=commands.getstatusoutput("/opt/ci123/apache/bin/apachectl "+str(arg))
                if(not apache_ret_status):
                        list=apache_ret.split("\n")
        for line in list:
                #tmp = line.strip()
                tmp = line
                result.append(tmp)
        return result

def get_apache_logslist(arg="0525"):
        """
        get apache infolist from shell
        CLI Example:
            salt '*' get_apache_info.get_apache_logslist
        """
        apache_num=commands.getoutput("ps -e |grep apache|grep -v grep|wc -l")
        if( not apache_num):
                return []
        result = []
        list = []
        #host_ip = commands.getoutput("ifconfig | awk -F'addr:|Bcast' '/Bcast/{print $2}'|grep -v '192.168'|head -n 1").strip()
        if(os.path.isdir('/opt/ci123/apache/logs')):
                apache_ret_status,apache_ret=commands.getstatusoutput("ls -l /opt/ci123/apache/logs/|sed '1d'|sed '/access/!d'|awk '{print $NF}'|grep '"+str(arg)+"'|awk -F'-' '{print $1}'")
                if(not apache_ret_status):
                        list=apache_ret.split("\n")
        for line in list:
                tmp = line.strip()
                result.append(tmp)
        return result
