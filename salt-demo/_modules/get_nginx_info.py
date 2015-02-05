#!/user/bin/env python

import os
import sys
import socket
import commands

def get_nginx_infolist(arg="-V"):
        """
        get nginx VirtualHost from shell
        CLI Example:
            salt '*' get_nginx_info.get_nginx_infolist
        """
        nginx_num=commands.getoutput("ps -e |grep nginx|grep -v grep|wc -l")
        if( not nginx_num):
                return {}
        result = []
	list = []
	#host_ip = commands.getoutput("ifconfig | awk -F'addr:|Bcast' '/Bcast/{print $2}'|grep -v '192.168'|head -n 1").strip()
	if(os.path.isfile('/opt/phpdba/nginx/sbin/nginx')):
        	nginx_ret_status,nginx_ret=commands.getstatusoutput("/opt/phpdba/nginx/sbin/nginx "+str(arg))
		if(not nginx_ret_status):
			list=nginx_ret.split("\n")
	for line in list:
		#tmp = line.strip()
		tmp = line
		result.append(tmp)
        return result
