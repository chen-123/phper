#!/user/bin/env  python2.6
#encoding=utf-8 
import sys
import salt.grains.core
import salt.config
import os
#import MySQLdb
import commands

reload(sys) 
sys.setdefaultencoding('utf-8') 

def System_info():
	'''
        echo System_info
        CLI Example:
            salt '*' info_sys_py_sh.System_info
        '''
	__opts__ = salt.config.client_config('/etc/salt/minion')

	id = __opts__.get('id')
	hostname=salt.grains.core.hostname()['fqdn']
	for ip in salt.grains.core.ip4()['ipv4']:
		if not ip.startswith('127') and not ip.startswith('192'):
			hostip=ip
	cpuinfo=salt.grains.core.os_data()['cpu_model']
	meminfo=salt.grains.core.os_data()['mem_total']
	saltversion=salt.grains.core.saltversion()['saltversion']
	pythonversion=commands.getoutput('python -V').strip()
	os=salt.grains.core.os_data()['osfullname'] + salt.grains.core.os_data()['osrelease']
	kernelrelease=salt.grains.core.os_data()['kernelrelease']
	if id!='linode_66':
		biosreleasedate=salt.grains.core.os_data()['biosreleasedate']
		productname=salt.grains.core.os_data()['productname']
		serialnumber=salt.grains.core.os_data()['serialnumber']
	else:
		biosreleasedate='xen'
		productname='xen'
		serialnumber='xen'
	nodename=salt.grains.core.os_data()['nodename']
	cpuarch=salt.grains.core.os_data()['cpuarch']
	defaultencoding=salt.grains.core.locale_info()['defaultencoding']
	defaultlanguage=salt.grains.core.locale_info()['defaultlanguage']

	insert_sql = 'insert into salt_system_info values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' % ('"'+str(id)+'"','"'+str(hostname)+'"','"'+str(hostip)+'"','"'+str(cpuinfo)+'"','"'+str(meminfo)+'"','"'+str(saltversion)+'"','"'+str(pythonversion)+'"','"'+str(os)+'"','"'+str(kernelrelease)+'"','"'+str(biosreleasedate)+'"','"'+str(productname)+'"','"'+str(nodename)+'"','"'+str(cpuarch)+'"','"'+str(serialnumber)+'"','"'+str(defaultencoding)+'"','"'+str(defaultlanguage)+'"','"'+str('one')+'"')
	#tmp=commands.getoutput('/opt/ci123/mysql/bin/mysql -h saltstack.ci123.com -u ci123sa -p"fuyuansalt" -Dsaltstack -e \''+insert_sql+'\'')	
	return insert_sql

	#conn=MySQLdb.connect(host='saltstack.ci123.com',user='ci123sa',passwd='fuyuansalt',db='saltstack',port=3306,charset='utf8')
	#cursor=conn.cursor()
	#cursor.execute('insert into salt_system_info values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' % ('"'+str(hostname)+'"','"'+str(hostip)+'"','"'+str(cpuinfo)+'"','"'+str(meminfo)+'"','"'+str(saltversion)+'"','"'+str(pythonversion)+'"','"'+str(os)+'"','"'+str(kernelrelease)+'"','"'+str(biosreleasedate)+'"','"'+str(productname)+'"','"'+str(nodename)+'"','"'+str(cpuarch)+'"','"'+str(serialnumber)+'"','"'+str(defaultencoding)+'"','"'+str(defaultlanguage)+'"','"'+str('one')+'"'))
	#conn.commmit()
	#cursor.close()
	#conn.close()
