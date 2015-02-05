#!/usr/bin python2.6
# coding:utf-8
# blog.phpdba.com
# author: chen-123

import paramiko
import pexpect
import commands
import re
import time
import ConfigParser
import string, os, sys
from datetime import *
from email.mime.text import MIMEText
import socket
import smtplib,time
import logging
import datetime
import getopt
from distutils.sysconfig import get_python_lib

reload(sys)
sys.setdefaultencoding('utf-8')

class NewClient(paramiko.SSHClient):
	""" 使用paramiko模块，远程登录服务器执行脚本"""
	def call(self, command, bufsize=-1):
		"""paramiko 执行返回脚本输出"""
		paramiko.util.log_to_file('logs/paramiko_'+time.strftime('%Y%m%d',time.localtime(time.time()))+'.log')
		chan = self._transport.open_session()
		chan.exec_command(command)
		stdin = chan.makefile('wb', bufsize)
		stdout = chan.makefile('rb', bufsize)
		stderr = chan.makefile_stderr('rb', bufsize)
		status = chan.recv_exit_status()
		return stdin, stdout, stderr, status

def batch_ssh_paramiko(host,port,user,passwd,key,cmd):
	"""通过调用paramiko模块函数，执行脚本，并返回结果"""
	try:
		scp_cmd(host,port=port,user=user,passwd=passwd,key=key,source_path=SourcePath,dest_path=DestPath,limit=1024,timeout=60)
		tc = NewClient()
                tc.load_system_host_keys()
                tc._policy = paramiko.AutoAddPolicy()
		if Debug :
			print host+"==="+port+"==="+user+"==="+passwd+"==="+key+"==="+cmd
                tc.connect(host,port=int(port), username=user, password=passwd,key_filename=key)
		stdin, stdout, stderr, status = tc.call(cmd)
		data = stdout.read()
		list_d = data.split('\n')
		if Debug :
			for item in data.split('\n'):
				print item.encode('utf-8')
		return list_d
	except Exception ,e:
		if Debug :
                	print e
		return ''

def scp_cmd(host,port="22",user="root",passwd="password",key="/root/.ssh/id_rsa",source_path="/tmp/chen-123.sh",dest_path="/tmp/",limit=1024,timeout=60):
	"""通过scp_cmd将脚本传输到目标服务器"""
	try :
		if os.path.exists(source_path) and os.path.isfile(source_path) :
			scp = pexpect.spawn('/usr/bin/scp -l %s -P %s -i%s %s %s@%s:%s' % (limit, port, key,source_path,user,host,dest_path),timeout=timeout)
			i = scp.expect(["assword","yes/no",'FATAL','No route to host','Connection Refused','Permission denied','Connection refused','Host key verification failed','Illegal host key','Connection Timed Out','Bad port','Interrupted system call'])
			if i == 0 :
				scp.sendline(passwd)
			elif i == 1 :
				scp.sendline('yes')
			else :
				scp.close(force=True)	

			#ii = scp.expect([']',pexpect.EOF, pexpect.TIMEOUT])
			ii = scp.expect(["100%",pexpect.EOF, pexpect.TIMEOUT])
			if ii == 0 :
				scp.sendline("exit")
				if Debug :
					print "scp 传输完毕"
	except pexpect.EOF:	
		scp.sendline("exit")
		if Debug :
			print "scp 传输完毕"
	except Exception ,e:
		if Debug :
			print e
			print "scp 传输失败"
	


#def ssh_cmd(host,port,user,passwd,key,cmd,logger,timeout=60,command_file_path="command.txt",is_Batch=False):
	#"""ssh 远程登录执行命令模块"""
	#print "密码登录方式：/usr/bin/ssh -o GSSAPIAuthentication=no -l%s -p%s %s" % (user, port, host)
	#print '密钥登录方式：/usr/bin/ssh -o GSSAPIAuthentication=no -l%s -p%s -i%s %s' % (user, port, key, host)
	#ssh = pexpect.spawnu('/usr/bin/ssh -o GSSAPIAuthentication=no -l%s -p%s %s' % (user, port, host),timeout=timeout)
	#ssh = pexpect.spawn('/usr/bin/ssh -o GSSAPIAuthentication=no -l%s -p%s -i%s %s' % (user, port, key, host),timeout=timeout)
	#print cmd
	#print key
	#print is_Batch

def ssh_cmd(host,port,user,passwd,key,cmd,logger,timeout=60,command_file_path="command.txt",is_Batch=False):
	"""ssh 远程登录执行命令模块"""

	try :
		if passwd.strip() == "" and user =="root" :
			logger.info("密码登录方式：/usr/bin/ssh -o GSSAPIAuthentication=no -l%s -p%s %s" % (user, port, host))
			ssh = pexpect.spawn('/usr/bin/ssh -o GSSAPIAuthentication=no -l%s -p%s %s' % (user, port, host),timeout=timeout)
		else:
			logger.info('密钥登录方式：/usr/bin/ssh -o GSSAPIAuthentication=no -l%s -p%s -i%s %s' % (user, port, key, host))
			ssh = pexpect.spawn('/usr/bin/ssh -o GSSAPIAuthentication=no -l%s -p%s -i%s %s' % (user, port, key, host),timeout=timeout)

		r = ''

        	i = ssh.expect(["assword","yes/no","]",'FATAL','No route to host','Connection Refused','Permission denied','Connection refused','Host key verification failed','Illegal host key','Connection Timed Out','Bad port','Interrupted system call'])
		ssh.setecho(False)
		#ssh.setecho(True)
		### 匹配到 password ，表明接下来要输入密码### 
        	if i == 0 :
        		ssh.sendline(passwd)
			ii = ssh.expect([']',pexpect.EOF, pexpect.TIMEOUT])
			if ii != 0 :
				logger.error("密码错误！原因：" + str(ii))
                        	ssh.close(force=True)
				#sys.exit(1)
			ssh_sendline(ssh,host,cmd,logger,command_file_path,is_Batch)

		### 匹配到 continue connecting (yes/no)? ,输入yes继续。
        	elif i == 1 :
        		ssh.sendline('yes')
			ii = ssh.expect([']',pexpect.EOF, pexpect.TIMEOUT])
                        if ii != 0 :
                                print "密钥不可用，请检查! index = " + str(ii)
				logger.error("密钥不可用，请检查! 原因： " + str(ii))
                                ssh.close(force=True)
				#sys.exit(1)
			
			ssh_sendline(ssh,host,cmd,logger,command_file_path,is_Batch)
		
		### 匹配到 ] ,登录成功，可以执行需要执行的命令。
		elif i == 2 :
			#print "开始执行命令："+str(cmd)
			ssh_sendline(ssh,host,cmd,logger,command_file_path,is_Batch)
			#print "脚本执行完毕退出！"
		else:
			print "不能登录服务器："+ str(host) +" 请核对服务器IP、端口、帐号和密码。原因："+ str(i) 
			ssh.close(force=True)
			logger.error("不能登录服务器："+ str(host) +" 请核对服务器IP、端口、帐号和密码。原因："+ str(i))
			#sys.exit(1)
		
		ssh.sendline("exit")
		r = ssh.read()

		r_list = []
		for tmp in r.split("\n"):
			if tmp.find("["+user) :
				if len(tmp.split("["+user)) > 1 :
					r_list.append("["+user+tmp.split("["+user)[1].strip())
				else :
					r_list.append(tmp.strip().replace("ESC[HESC[2J",""))

		rr = "\n".join(r_list)

		if Debug :
			print rr 

		logger.info("服务器："+host+" 执行结果：\n"+str(rr))
		ssh.expect(pexpect.EOF)
		ssh.close(force=True)
		logger.info(host+"操作完成，退出服务器！")
		print host +" shell cmd ok"
	except pexpect.EOF:
		if Debug :
			print "不能登录服务器："+ str(host) +" 请核对服务器IP、端口、帐号和密码。"
		logger.error("不能登录服务器："+ str(host) +" 请核对服务器IP、端口、帐号和密码。")
        	ssh.close(force=True)
		#sys.exit(1)
	except pexpect.TIMEOUT:
		if Debug :
			print "登录服务器："+ str(host) +"超时，请核对服务器IP、端口、帐号和密码。"
                logger.error("登录服务器："+ str(host) +"超时，请核对服务器IP、端口、帐号和密码。")
                ssh.close(force=True)
                #sys.exit(1)
	except Exception ,e:
		if Debug :
			print e
			print "登录服务器："+ str(host) +"异常，请核对服务器IP、端口、帐号和密码。"
                logger.error("登录服务器："+ str(host) +"异常，请核对服务器IP、端口、帐号和密码。")
                ssh.close(force=True)
                #sys.exit(1)
	return r

def ssh_sendline(ssh,host,cmd,logger,command_file_path="command.txt",is_Batch=False):
	"""封装ssh.sendline函数处理逻辑"""
	
        if ssh :
                if is_Batch and os.path.exists(command_file_path) and os.path.isfile(command_file_path) :
			logger.info(host+" 开始执行批量命令：")
                        fc = open(command_file_path,"r")
                        for eachline in fc:
                                if not eachline.strip().startswith("#") :
                                        command = eachline.strip()
                                        print command
                                        if command != "" :
                                        	ssh.sendline(command)
						#ii = ssh.expect(['yes/no',pexpect.EOF, pexpect.TIMEOUT])
                        			#if ii != 0 :
                                		#	logger.error("不可用，请检查! 原因： " + str(ii))
                                		#	ssh.close(force=True)
						#else:
						#	ssh.sendline("yes")
					
                                                logger.info("\t\t\t\t    "+command)
                                	else :
                                        	logger.errro("请检查"+command_file_path+"命令列表")
                        fc.close()
			if cmd.strip() :
				logger.info("\t\t\t\t    "+cmd)
				ssh.sendline(cmd)
				#ii = ssh.expect(['yes/no',pexpect.EOF, pexpect.TIMEOUT])
                                #if ii != 0 :
                                #	logger.error("不可用，请检查! 原因： " + str(ii))
                                #	ssh.close(force=True)
                                #else:
                                #	ssh.sendline("yes")
                else :
                        logger.info(host+" 开始执行命令："+str(cmd))
                        ssh.sendline(cmd)
			#ii = ssh.expect(['yes/no',pexpect.EOF, pexpect.TIMEOUT])
                        #if ii != 0 :
                        #	logger.error("不可用，请检查! 原因： " + str(ii))
                        #        ssh.close(force=True)
                        #else:
                        #        ssh.sendline("yes")
	else :
		logger.errro("请检查ssh_sendline函数ssh参数")

	#ssh.send("\n")

       	logger.info(host+" 执行完毕退出！")

def iconv():
	"""转码"""
	iconv_status,iconv_ret = commands.getstatusoutput("/bin/sh iconv.sh /tmp/iconv.txt")
	if iconv_status == 0 :
		return iconv_ret
	else :
		return 1


def init_log(logger_name,file_name):
	"""初始话日志"""
	global Flag
	global logger

	if not os.path.exists("logs") :
		os.mkdir("logs")

	if not Flag and not logger :
		logger = logging.getLogger(logger_name)
        	logger.setLevel(logging.DEBUG)
       		fh = logging.FileHandler("logs/"+file_name+"_"+time.strftime('%Y%m%d',time.localtime(time.time()))+".log")
       		fh.setLevel(logging.DEBUG)
       		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
       		fh.setFormatter(formatter)
       		logger.addHandler(fh)
		if os.path.getsize("logs/"+file_name+"_"+time.strftime('%Y%m%d',time.localtime(time.time()))+".log") <= 0 :
        		logger.debug("debug message")
        		logger.info("info message")
        		logger.warn("warn message")
        		logger.error("error message")
        		logger.critical("critical message")
		Flag=True
	
	return logger

def batch_iplist(iplist_file_path,cmd,user="root",key="/root/.ssh/id_rsa",timeout=60,command_file_path="command.txt",is_Batch=False):
	"""通过ip列表批量执行命令"""

	starttime = datetime.datetime.now()
        #try:
        f = open(iplist_file_path,"r")
        for eachline in f:
                if not eachline.strip().startswith("#") and not eachline.strip().startswith("192") :
		#if not eachline.strip().startswith("#") and eachline.strip().startswith("192") :
                        server_info = eachline.strip().split(" ")
                        host = server_info[0].strip()
                        port = server_info[1].strip()
			if user == "":
                        	user = server_info[2].strip()
                        passwd = server_info[3].strip()
			if passwd == "":
				passwd = server_info[4].strip()
			if Debug :
                        	print host+" "+port+" "+user+" "+passwd
			ssh_cmd(host,port,user,passwd,key,cmd,logger,timeout,command_file_path,is_Batch)
        f.close()
        endtime = datetime.datetime.now()
	print (endtime-starttime).seconds
	#except Exception,e:
	#       print Exception,e

	print "批量执行完毕"


def batch_ssh_mysql(iplist_file_path,cmd,user="root",key="/root/.ssh/id_rsa",timeout=60,command_file_path="command.txt",is_Batch=False):
        """通过ip列表批量获取mysql信息"""

        starttime = datetime.datetime.now()
        #try:
        f = open(iplist_file_path,"r")
        for eachline in f:
                if not eachline.strip().startswith("#") and not eachline.strip().startswith("192") :
                #if not eachline.strip().startswith("#") and eachline.strip().startswith("192") :
                        server_info = eachline.strip().split(" ")
                        host = server_info[0].strip()
                        port = server_info[1].strip()
                        if user == "":
                                user = server_info[2].strip()
                        passwd = server_info[3].strip()
                        if passwd == "":
                                passwd = server_info[4].strip()
                        print host+" "+port+" "+user+" "+passwd
			
			if is_Batch and os.path.exists(command_file_path) and os.path.isfile(command_file_path) :
                        	logger.info(host+" paramiko 开始执行批量命令：")
                        	fc = open(command_file_path,"r")
                        	for eachline in fc:
                                	if not eachline.strip().startswith("#") :
                                        	command = eachline.strip()
                                        	if command != "" :
							re=batch_ssh_paramiko(host,port,user,passwd,key,cmd=command)
                                                	logger.info("\t\t\t\t    "+command)
                                        	else :
                                                	logger.errro("请检查"+command_file_path+"命令列表")
                        	fc.close()
                        	if cmd.strip() :
                                	logger.info("\t\t\t\t    "+cmd)
					re = batch_ssh_paramiko(host,port,user,passwd,key,cmd)
                	else :
                        	logger.info(host+" 开始执行命令："+str(cmd))
				re = batch_ssh_paramiko(host,port,user,passwd,key,cmd)

			logger.info(host+" 执行完毕")
	
        f.close()
        endtime = datetime.datetime.now()
        print (endtime-starttime).seconds
        #except Exception,e:
        #       print Exception,e

        print "批量执行完毕"

def batch_iptable_func(sub_domain,iptable_config_ini="iptable_config.ini",iptable_iplist_file="iptable_iplist_file.txt",iptable_ban_ip="61.164.143.115") :
	"""通过项目域名，批量封禁那些恶意IP"""

	if not sub_domain or not os.path.exists(iptable_config_ini) :
		print "亲，项目域名未传入或者前端配置文件不存在，请检查。。。"
		logger.error("亲，项目域名未传入或者前端配置文件不存在，请检查。。。")
		sys.exit(1)

	config_ini = ConfigParser.ConfigParser()
        config_ini.read(iptable_config_ini)
        config_list = config_ini.sections()
	subdomain_flag = False
        for item in config_list:
		if item == sub_domain :
			subdomain_flag = True

	if subdomain_flag :	
		user = config_ini.get(sub_domain,'user')
		passwd = config_ini.get(sub_domain,'passwd')
                front_end = config_ini.get(sub_domain,'front-end')
		command = config_ini.get(sub_domain,'command')
		auth_key = config_ini.get(sub_domain,'auth-key')
		front_info = front_end.split(',')
		for ip_str in front_info:
			host_port = ip_str.strip().split(":")	
			if Debug :
				host = "192.168.0.28"
				port = '22'
			else :
				host = host_port[0]
				port = host_port[1]

			if Debug and iptable_iplist_file :
				print "iptable_iplist_file:"+iptable_iplist_file

			print "host:"+host+" port:"+port
			if not check_ip(host):
				logger.error("IP地址无效："+host+"请检查该服务器是否下架或者配置出错")
				return "请检查前端代理主机IP是否有效"

			logger.info("host:"+host+" port:"+port)

			if os.path.exists(iptable_iplist_file) and os.path.isfile(iptable_iplist_file) :
				logger.info("iptable_iplist_file:"+iptable_iplist_file)
				iplist = open(iptable_iplist_file,'r')
				for eachline in iplist.readlines():
					logger.info("iptable_ban_ip:"+eachline.strip())
					exec_command = command.replace('%s',eachline.strip())
					logger.info("iptable_cmd:"+exec_command)
					if check_ip(eachline.strip()):
						ssh_cmd(host,port,user,passwd,auth_key,exec_command,logger,60,"",False)
					else :
						logger.error("IP地址无效："+eachline.strip())
				iplist.close()
				if iptable_ban_ip :
					exec_command = command.replace('%s',iptable_ban_ip)
					logger.info("iptable_ban_ip:"+iptable_ban_ip)
					logger.info("iptable_cmd:"+exec_command)
					if check_ip(iptable_ban_ip):
						ssh_cmd(host,port,user,passwd,auth_key,exec_command,logger,60,"",False)
					else:
						logger.error("IP地址无效："+iptable_ban_ip)
			elif iptable_ban_ip :
				logger.info("iptable_ban_ip:"+iptable_ban_ip)
                                exec_command = command.replace('%s',iptable_ban_ip)
                                logger.info("iptable_cmd:"+exec_command)
				if check_ip(iptable_ban_ip):
                                	ssh_cmd(host,port,user,passwd,auth_key,exec_command,logger,60,"",False)
				else :
					logger.error("IP地址无效："+iptable_ban_ip)
			else :
				if Debug :
					print "iptable_iplist_file:"+iptable_iplist_file+"不存在"
				logger.error("iptable_iplist_file:"+iptable_iplist_file+"不存在")


		if Debug :
			print "项目："+sub_domain+"; 用户名："+user+"; 前端："+front_end+" ; 命令："+command
                	#print "项目："+sub_domain+"; 用户名："+user+"; 密码："+passwd+"; 前端："+front_end+" ; 命令："+command+"; 密钥："+auth_key
	else :
		print "亲，"+sub_domain+"未配置,请联系管理员。。。"
		logger.error("亲，"+sub_domain+"未配置,请联系管理员")
		sys.exit(1)

def check_ip(ipaddr):
	addr=ipaddr.strip().split('.') 
        if len(addr) != 4:  
		if Debug : 
        		print "IP地址错误:"+ipaddr+"（不是由四组数字组成）"
		logger.info("IP地址错误:"+ipaddr+"（不是由四组数字组成）")
                return False
 
        for i in range(4): 
                try: 
                        addr[i]=int(addr[i]) 
                except:
			if Debug : 
                        	print "IP地址错误:"+ipaddr+"（不是由四组数字组成）"
			logger.info("IP地址错误:"+ipaddr+"（不是由四组数字组成）")
                        return False

                if addr[i]<=255 and addr[i]>=0:     
                        pass
                else: 
			if Debug :
                        	print "IP地址错误:"+ipaddr+"（地址不合法，大于255）"
			logger.info("IP地址错误:"+ipaddr+"（地址不合法，大于255）")
                        return False 
                i+=1
        else: 
		if Debug :
                	print "check ip address success!"
		return True


	
def usage():
	#print get_python_lib()
	print """
	### 执行批量命令 调用方式
        batch_iplist("iplist.txt",'who',"root","/root/.ssh/id_rsa",60,"command.txt",True)
        ### 执行单个命令 调用方式
        batch_iplist("iplist.txt",'who',"root","/root/.ssh/id_rsa",60,"command.txt",False)
	### iptable 功能模块
	1、通过读取iptable_iplist_file.txt文件中ip列表，批量封禁IP
	python2.6 batch_ssh.py -I --iptable_config_ini=iptable_config.ini --sub_domain=www.phpdba.com  --iptable_iplist_file=iptable_iplist_file.txt	
	2、直接通过-s将要封禁IP，传入脚本
	python2.6 batch_ssh.py -I --iptable_config_ini=iptable_config.ini --sub_domain=www.phpdba.com  -s 123.123.123.123
	3、同时封禁iptable_iplist_file.txt和-s指定IP
	python2.6 batch_ssh.py -I --iptable_config_ini=iptable_config.ini --sub_domain=www.phpdba.com  -s 123.123.123.123 --iptable_iplist_file=iptable_iplist_file.txt

	### 批量执行命令模块
	1、以dev 权限登录iplist.txt中ip，同时批量执行command.txt中定义系列命令及command定义命令
	python2.6 batch_ssh.py -B --batch_iplist_file=iplist.txt --batch_commandlist_file=command.txt --command="ps aux|grep python" --batch_user=dev --batch_auth_key=dev_id_rsa
	2、以dev 权限登录iplist.txt中ip，执行command.txt中系列命令
	python2.6 batch_ssh.py -B --batch_iplist_file=iplist.txt --batch_commandlist_file=command.txt --batch_user=dev --batch_auth_key=dev_id_rsa
	3、以dev权限登录iplist.txt中ip，只执行command定义命令
	python2.6 batch_ssh.py -B --batch_iplist_file=iplist.txt --command="ps aux|grep python" --batch_user=dev --batch_auth_key=dev_id_rsa
	4、以root权限登录iplist.txt中ip，批量执行command.txt文件中定义的系列命令
	python2.6 batch_ssh.py -B --batch_iplist_file=iplist.txt --batch_commandlist_file=command.txt
	5、以root权限登录iplist.txt中ip，执行command定义的命令
	python2.6 batch_ssh.py -B --batch_iplist_file=iplist.txt --command="ps aux|grep python"	
	6、以root权限登录iplist.txt中ip，同时批量执行command.txt中定义系列命令及command定义命令
	python2.6 batch_ssh.py -B --batch_iplist_file=iplist.txt --batch_commandlist_file=command.txt --command="ps aux|grep python"
	### 批量获取mysql信息
	1、以root权限登录iplist.txt中ip，批量执行command.txt文件中定义的系列命令
	python2.6 batch_ssh.py -M --batch_iplist_file=iplist.txt --batch_commandlist_file=command.txt
	
	"""

if __name__ == '__main__':
	#scp_cmd(host='192.168.1.114',port="29622",user="root",passwd="password",key="/root/.ssh/id_rsa",source_path="/tmp/chen-123.sh",dest_path="/tmp/",limit=1024,timeout=60)
	
	#全局变量初始化
	Flag = False
        logger = False
	Debug = True
	#Debug = False
	SourcePath = '/tmp/chen-123.sh'
	DestPath = '/tmp/'


	try :
		# 日志初始化
		logger = init_log("simple_log","ssh_cmd_batch")

		opts, args = getopt.getopt(sys.argv[1:], "hIBMo:s:c:", ["help","iptable","batch","mysql_info","batch_user=","batch_auth_key=","command=","batch_iplist_file=","batch_commandlist_file=","sub_domain=","iptable_config_ini=","iptable_iplist_file="])

		if Debug :
			print("============ opts ==================");         
        		print(opts) 
        		print("============ args ==================");  
	        	print(args) 
		
		Batch_cmd = False
		iptable_func = False
		Batch_mysql = False
		batch_user = ""
		batch_auth_key = ""
		command = ""
		batch_iplist_file = ""
		batch_commandlist_file = ""
		sub_domain = ""
		iptable_config_ini = ""
		iptable_iplist_file = ""
		iptable_ban_ip = ""
 
		for k,value in opts:

			if k in ('-h','--help'):
				usage()
				sys.exit(1)	
		
			if k in ("-I","--iptable") :
				iptable_func = True
			elif k in ("-B","--batch") :
				Batch_cmd = True
			elif k in ("-M","--mysql_info") :
				Batch_mysql = True
			elif k == "--batch_iplist_file" :
				batch_iplist_file = value
			elif k == "--batch_commandlist_file" :
				batch_commandlist_file = value
			elif k == "--sub_domain" :
				sub_domain = value
			elif k == "--iptable_config_ini" :
                                iptable_config_ini = value
			elif k == "--iptable_iplist_file" :
				iptable_iplist_file = value
			elif k == "-s" :
				iptable_ban_ip = value
			elif k == "--batch_user" :
				batch_user = value
			elif k == "--batch_auth_key" :
				batch_auth_key = value
			elif k in ("-c","--command") :
				command = value
			else :
				print "亲，功能正在完善，目前不支持 。。。"
				usage()
				sys.exit(1)

		if iptable_func and sub_domain and iptable_config_ini and iptable_ban_ip and iptable_iplist_file :
			print "iptable_ban_ip && iptable_iplist_file"
			batch_iptable_func(sub_domain,iptable_config_ini,iptable_iplist_file,iptable_ban_ip)
		elif iptable_func and sub_domain and iptable_config_ini and iptable_ban_ip :
			print "iptable_ban_ip"
			batch_iptable_func(sub_domain,iptable_config_ini,iptable_iplist_file,iptable_ban_ip)
		elif iptable_func and sub_domain and iptable_config_ini and iptable_iplist_file :
			print "iptable_iplist_file"
			batch_iptable_func(sub_domain,iptable_config_ini,iptable_iplist_file,iptable_ban_ip)
		elif Batch_cmd and batch_iplist_file and batch_commandlist_file and not batch_user :
			print "批量执行 root 权限"
			batch_iplist(iplist_file_path=batch_iplist_file,cmd=command,command_file_path=batch_commandlist_file,is_Batch=True)
		elif Batch_cmd and batch_user and batch_auth_key and batch_iplist_file and batch_commandlist_file :
			print "批量执行 "+batch_user+" 权限"
                        batch_iplist(iplist_file_path=batch_iplist_file,cmd=command,user=batch_user,key=batch_auth_key,command_file_path=batch_commandlist_file,is_Batch=True)
		elif Batch_cmd and batch_iplist_file and command and not batch_user :
			print "root 权限执行："+command
			batch_iplist(iplist_file_path=batch_iplist_file,cmd=command,command_file_path=batch_commandlist_file,is_Batch=False)
		elif Batch_cmd and batch_iplist_file and command and batch_user and batch_auth_key :
			print batch_user+"  权限执行："+command
                        batch_iplist(iplist_file_path=batch_iplist_file,user=batch_user,key=batch_auth_key,cmd=command,command_file_path=batch_commandlist_file,is_Batch=False)
		elif Batch_mysql and batch_iplist_file and batch_commandlist_file :
                        print "批量执行 root 权限"
			batch_ssh_mysql(iplist_file_path=batch_iplist_file,cmd=command,command_file_path=batch_commandlist_file,is_Batch=True)
			#batch_ssh_mysql(iplist_file_path,cmd,user="root",key="/root/.ssh/id_rsa",timeout=60,command_file_path="command.txt",is_Batch=False):
		else :
			print "亲，功能模块使用问题(比如：缺少参数)，请联系wp8155562@gamil.com"

	except getopt.GetoptError :
		print "亲，该功能正在开发，期待下个版本为您提供！！！"
	
