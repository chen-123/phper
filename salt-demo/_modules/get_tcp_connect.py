#!/usr/bin/env python

import subprocess
def tcpconnect():
	'''
	get tcp connect status
        CLIExample:
		salt '*' get_tcp_connect.tcpconnect
	'''
	tcp_status=subprocess.Popen("netstat -an|awk '/^tcp/ {++S[$NF]} END{for(a in S) print a,S[a]}'",stdout=subprocess.PIPE,shell=True)
	return tcp_status.stdout.read()
