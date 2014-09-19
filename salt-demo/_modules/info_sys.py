#!/user/bin/env  python2.6
#encoding=utf-8 

import sys
import salt
import salt.client
import salt.minion
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
            salt '*' info_sys.System_info
        '''
	
	__opts__ = salt.config.minion_config('/etc/salt/minion')
	id=__opts__['id']
	#local = salt.client.LocalClient(__opts__['conf_file'])
	#local = salt.client.LocalClient()
	caller = salt.client.Caller()
	ret = caller.sminion.functions['grains.items']()
	#ret = local.cmd(id, 'grains.items', [])
	hostname=ret['fqdn']
	for ip in ret['ipv4']:
		if not ip.startswith('127'):# and not ip.startswith('192'):
			hostip=ip
	cpuinfo=ret['cpu_model']
	meminfo=ret['mem_total']
	saltversion=ret['saltversion']
	pythonversion=commands.getoutput('python -V')
	os=ret['osfullname'] + ret['osrelease']
	kernelrelease=ret['kernelrelease']
	biosreleasedate='unknown' if not ret.has_key('biosreleasedate') else ret['biosreleasedate']
	productname='unknown' if not ret.has_key('productname') else ret['productname']
	nodename=ret['nodename']
	cpuarch=ret['cpuarch']
	#max_open_file=salt.grains.core.os_data()['max_open_file']
	serialnumber='unknown' if not ret.has_key('serialnumber') else ret['serialnumber']
	defaultencoding=ret['defaultencoding']
	defaultlanguage=ret['defaultlanguage']

	insert_sql='insert into salt_system_info values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' % ('"'+str(id)+'"','"'+str(hostname)+'"','"'+str(hostip)+'"','"'+str(cpuinfo)+'"','"'+str(meminfo)+'"','"'+str(saltversion)+'"','"'+str(pythonversion)+'"','"'+str(os)+'"','"'+str(kernelrelease)+'"','"'+str(biosreleasedate)+'"','"'+str(productname)+'"','"'+str(nodename)+'"','"'+str(cpuarch)+'"','"'+str(serialnumber)+'"','"'+str(defaultencoding)+'"','"'+str(defaultlanguage)+'"','"'+str('one')+'"')

	return insert_sql
