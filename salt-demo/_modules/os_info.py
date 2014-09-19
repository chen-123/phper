#!/user/bin/env python

import subprocess
import os
import commands
import sys
import time

def echo_os_type():
	'''
	echo os type infomation
        CLI Example:
	    salt '*' os_info.echo_os_type
	'''
	return os.uname()
def get_cpu_number():
	'''
        get cpu number
        CLI Example:
            salt '*' os_info.get_cpu_number
        '''
	cpu_num=subprocess.Popen("grep -c 'model name' /proc/cpuinfo",stdout=subprocess.PIPE,shell=True)
	return cpu_num.stdout.read().rstrip('\n')
def get_cpu_physical_number():
        '''
        get cpu number
        CLI Example:
            salt '*' os_info.get_cpu_physical_number
        '''
        cpu_physical_num=subprocess.Popen("cat /proc/cpuinfo|grep 'physical id'|sort -rn|uniq -c|wc -l",stdout=subprocess.PIPE,shell=True)
        return cpu_physical_num.stdout.read().rstrip('\n')
def get_mem_total():
	'''
        get total mem
        CLI Example:
            salt '*' os_info.get_mem_total
        '''
	total_mem=commands.getoutput('cat /proc/meminfo|grep MemTotal|awk \'{printf "%d\\n",$2/1024/1000+0.5}\'')
	return total_mem
def _read_mount_list():
        """
        Read the current system filesystem mount_list from /proc/mounts.
	CLI Example:
            salt '*' os_info._read_mount_list
        """
        return_lines=[]
        try:
                fd = open("/proc/mounts", 'r')
                lines = fd.readlines()
        finally:
                if fd:
                   fd.close()
        for line in lines:
                l = line.split()
                if l[0].startswith('/') or l[0].startswith('192'):
                        return_lines.append(line)
        return return_lines

def get_mount_list():
        """
        get mount list
	CLI Example:
            salt '*' os_info.get_mount_list
        """
        dict={}
        list=_read_mount_list()
        for line in list:
                tmp=line.split()
                dict[tmp[0]]=tmp[1]
        return dict
