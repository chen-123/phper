#!/usr/bin/env python

import subprocess
def mysql_threadnum():
	'''
	get tcp connect status
        CLIExample:
		salt'*' get_mysqlthread_num.mysql_threadnum
	'''
	mysqlthreadnum=subprocess.Popen("ps aux|grep mysql|grep 'socket'|grep -v 'grep'|wc -l",stdout=subprocess.PIPE,shell=True)
	return mysqlthreadnum.stdout.read().rstrip('\n')
