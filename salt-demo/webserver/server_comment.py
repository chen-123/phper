#!/usr/bin/env python2.6
#-*- coding: UTF-8 -*-

import os 
localDir = os.path.dirname(__file__) 
absDir = os.path.join(os.getcwd(), localDir) 
import cherrypy 
class SaltWebServiceDemo(object):

    def index(self):
	"""
	Demo 默认首页
	"""
 
        return """
	<!DOCTYPE HTML> 
        <html>
	<head>
	<meta charset="utf-8" />
	<title>demo</title>
	</head>
	 <body> 
            <h2>demo</h2> 
            <form action="commend" method="post"> 
	    Client：<select name="client">
                <option value="*">default</option>
		<option value="local_28">内网28</option>
		<option value="local_53">内网53</option>
		<option value="local_18">内网18</option>
	    </select><br/>
	    Action：<select name="action">
		<option value="default">default</option>
		<option value="cmd.run">cmd</option>
	    </select><br/>
            function: <input type="input" name="function" size="50" /> Statistics: <input type="checkbox"  name="status" /> <br /> 
            <input type="submit" /> 
            </form> 
        </body></html> 
        """ 
    index.exposed = True


    def comment_init(self, client, action, function):
	"""
	comment 初始化salt
	"""
	import salt.client
        import salt.config

        #__opts__ = salt.config.client_config(
        #            os.environ.get('SALT_MASTER_CONFIG', '/etc/salt/master'))

        #local = salt.client.LocalClient(__opts__['conf_file'])
        local = salt.client.LocalClient()
        #print local.cmd('local_19', 'cmd.run', [function])
        #return
        if function == "reboot" or function == "shutdown":
                return "ok"


        if action == 'cmd.run' :
                ret = local.cmd(client,'cmd.run' ,[function])
                #ret = local.cmd(client,'cmd.run' ,[function],  username="saltadmin", password='fuyuannoccjy', eauth='pam')
        else:
                ret = local.cmd(client,function)
                #ret = local.cmd(client,function,  username="saltadmin", password='fuyuannoccjy', eauth='pam')

	return ret


    def comment_html(self, container_js_out):
	"""
	comment 最终显示页面
	"""
	out = """
        <!DOCTYPE HTML>
        <html>
        <head>
        <meta charset="utf-8" />
        <title>demo result</title>
        <script type="text/javascript" src="http://webproxy.phpdba.com/js/jquery.min.js"></script>
        <script type="text/javascript" src="http://file2.phpdba.com/noc/js/highcharts.js"></script>
        <script type="text/javascript" src="http://file2.phpdba.com/noc/js/modules/exporting.js"></script>
        <script type="text/javascript">
        {container_js}
        </script>
        </head>
        <body>
            <div id="container" style="min-width: 310px; height: auto; margin: 0 auto"></div>
        </body>
        </html>"""
	return out.replace("{container_js}",container_js_out)

    def commend_container_js(self, client, series_str):
	"""
	Demo 饼图js代码
	"""
	container_js="""
        $(function () {$('#container').highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: 'Tcp Connect  {client}'
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    color: '#000000',
                    connectorColor: '#000000',
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'TCP CONNECTION',
            data: [
                {0}
            ]
        }]
        });
        });
        """
	container_js_str = container_js.replace("{0}",series_str)
        container_js_ret = container_js_str.replace("{client}",client)
	return container_js_ret

	
    def commend(self, client, action ,function, status=None):
	"""
	Demo 表单action处理页面
	"""
	 
	container_js_bar="""
	$(function () {
        $('#container').highcharts({
            chart: {
                type: '{type}',
		{height}
            },
            title: {
                text: '状态实时统计图'
            },
            subtitle: {
                text: 'Source: ci123.com'
            },
            xAxis: {
                categories: [{client_list}],
                title: {
                    text: null
                }
            },
            yAxis: {
                min: 0,
                title: {
                    text: '',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }
            },
            tooltip: {
                valueSuffix: ' '
            },
            plotOptions: {
                bar: {
                    dataLabels: {
                        enabled: true
                    }
                }
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'top',
		x: -40,
		y: 100,
                floating: true,
                borderWidth: 1,
                backgroundColor: '#FFFFFF',
                shadow: true
            },
            credits: {
                enabled: false
            },
            series: [{series}]
        });
    });
	"""

	ret = self.comment_init(client, action, function)
	
	if function == 'get_tcp_connect.tcpconnect':
		if client != '*':
			arr = ret[client].rstrip().split('\n')
			result = []
			result_str = ""
			for i in arr:
				tmp_i = i.split(' ')
				result.append("['"+tmp_i[0]+"',   "+tmp_i[1]+"]")
			series_str = ','.join(result)
			container_js_ret = self.commend_container_js(client, series_str)
			return self.comment_html(container_js_ret)
		else:
			client_list = list(ret.keys())
			client_list_str_tmp = "','".join(client_list)
			client_list_str = "'"+client_list_str_tmp+"'"
			series_dict = {}
			series_list = []
			option_list2 = ["TIME_WAIT","CLOSE_WAIT","FIN_WAIT1","FIN_WAIT2","ESTABLISHED","SYN_RECV","CLOSING","LAST_ACK","LISTEN","SYN_SENT"] 
			option_list_data = {}
			series_list_str = ""
			for option2 in option_list2:
				option_list_data[option2]=[]

			for client_id in client_list:
				arr_ser = ret[client_id].rstrip().split('\n')
				series_list_data_tmp = {}
				option_list = ["TIME_WAIT","CLOSE_WAIT","FIN_WAIT1","FIN_WAIT2","ESTABLISHED","SYN_RECV","CLOSING","LAST_ACK","LISTEN","SYN_SENT"]
				data_str = ""
				for j in arr_ser:
					tmp_j = j.split(' ')
					series_list_data_tmp[tmp_j[0]] = tmp_j[1]
					option_list_data[tmp_j[0]].append(str(tmp_j[1]))
					option_list.remove(tmp_j[0])

				for option in option_list:
					series_list_data_tmp[option] = 0
					option_list_data[option].append(str(0))

			for option3 in option_list2:
				option3_tmp_str = ','.join(option_list_data[option3])
				series_list.append("{ name:'%s',data:[%s]}" % (option3,option3_tmp_str))
				option3_str="{ name:'%s',data:[%s]}" % (option3,option3_tmp_str)
			series_list_str = ','.join(series_list)	
			series_list_str2 = container_js_bar.replace("{client_list}",client_list_str)
			series_list_str3 = series_list_str2.replace("{height}","height:5000")
			series_list_str4 = series_list_str3.replace("{type}","bar")
			container_js_bar_out = series_list_str4.replace("{series}",series_list_str)
			return self.comment_html(container_js_bar_out)	
	elif function == 'get_mysqlthread_num.mysql_threadnum' or function == 'os_info.get_mem_total':
		client_list = list(ret.keys())
                client_list_str_tmp = "','".join(client_list)
                client_list_str = "'"+client_list_str_tmp+"'"
		list_data = []
		for client_id in client_list:
			arr_ser = ret[client_id].rstrip().split('\n')
			list_data.append(str(ret[client_id]))
		if status == "on":
			list_data_cat = {}
			for data in list_data:
				list_data_cat[str(data)] = []
			for data in list_data:
				list_data_cat[str(data)].append(data)
		
			list_data_cat_str_list = []
			for key,values in list_data_cat.items():
				tmp_str = "{ name:'%s',data:[%s]}" % (str(key),len(values))
				list_data_cat_str_list.append(tmp_str)
			
			series_list_str = ','.join(list_data_cat_str_list)
			series_list_str2 = container_js_bar.replace("{client_list}","'统计 "+str(function+"'"))
		else:
			list_data_str = ','.join(list_data)

			if function == 'get_mysqlthread_num.mysql_threadnum':	
				series_list_str="{ name:'%s',data:[%s]}" % ("mysql 进程数统计",list_data_str)
			elif function == 'os_info.get_mem_total':
				series_list_str="{ name:'%s',data:[%s]}" % ("内存大小统计",list_data_str)

			series_list_str2 = container_js_bar.replace("{client_list}",client_list_str)
		if client != '*':
			series_list_str3 = series_list_str2.replace("{height}","height:400")
			series_list_str4 = series_list_str3.replace("{type}","column")
		else:
			if status == "on":
				series_list_str3 = series_list_str2.replace("{height}","height:400")
                        	series_list_str4 = series_list_str3.replace("{type}","column")
			else:
				series_list_str3 = series_list_str2.replace("{height}","height:1000")
				series_list_str4 = series_list_str3.replace("{type}","bar")
		container_js_bar_out = series_list_str4.replace("{series}",series_list_str)
		
		return self.comment_html(container_js_bar_out)
	elif function == 'os_info.get_cpu_physical_number' or function == 'os_info.get_cpu_number':
                client_list = list(ret.keys())
                client_list_str_tmp = "','".join(client_list)
                client_list_str = "'"+client_list_str_tmp+"'"
                list_data = []
                for client_id in client_list:
                        arr_ser = ret[client_id].rstrip().split('\n')
			if ret[client_id].isdigit():
                        	list_data.append(str(ret[client_id]))
			else:
				list_data.append(str(0))
                list_data_str = ','.join(list_data)
		item_num = {}
		series_list = []
		series_list_client = []
		if status == "on":
			for item in list_data:
				item_num[str(item)]=[]
			for item in list_data:
                        	item_num[str(item)].append(item)

			for key,values in item_num.items():
				tmp_str = "{ name:'%s',data:[%s]}" % (str(key)+" 个",len(values))
				series_list.append(tmp_str)
				series_list_client.append(str(key)+" 个cpu")

			series_list_str = ','.join(series_list)
			series_list_client_str_tmp = "','".join(series_list_client)
			series_list_client_str = "'"+str("CPU统计 ")+str(function)+"'"
			series_list_str2 = container_js_bar.replace("{client_list}",series_list_client_str)
			series_list_str3 = series_list_str2.replace("{height}","height:300")
			series_list_str4 = series_list_str3.replace("{type}","bar")	
		else:
			series_list_str="{ name:'%s',data:[%s]}" % (str("CPU 统计")+str(function),list_data_str)
			series_list_str2 = container_js_bar.replace("{client_list}",client_list_str)
			if client != '*':
				series_list_str3 = series_list_str2.replace("{height}","height:200")
				series_list_str4 = series_list_str3.replace("{type}","column")
			else:
				series_list_str3 = series_list_str2.replace("{height}","height:1000")
				series_list_str4 = series_list_str3.replace("{type}","bar")

                container_js_bar_out = series_list_str4.replace("{series}",series_list_str)

		return self.comment_html(container_js_bar_out)
	else:
		for key,value in ret.items():
			print(key,value)
		#return ret
		return function
    commend.exposed = True 


conf = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'tools.encode.on':True,
        'tools.encode.encoding':'utf8',
    },
}

if __name__ == '__main__': 
    cherrypy.quickstart(SaltWebServiceDemo(),'/',conf)
