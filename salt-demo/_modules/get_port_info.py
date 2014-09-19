#!/user/bin/env python

import os
import sys
import socket
import commands

def get_used_port_list():
        """
        get apache infolist from shell
        CLI Example:
            salt '*' get_port_info.get_used_port_list
        """
        result = []
        list = []
        #host_ip = commands.getoutput("ifconfig | awk -F'addr:|Bcast' '/Bcast/{print $2}'|grep -v '192.168'|head -n 1").strip()
        ret_status,ret=commands.getstatusoutput("netstat -nltp")
       	if(not ret_status):
        	list=ret.split("\n")
        for line in list:
                tmp = line.strip()
                result.append(tmp)
        return result
