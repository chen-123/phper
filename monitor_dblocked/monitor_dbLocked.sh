#!/bin/sh
#author:chen-123
#检查当前主机上mysql实例是否锁表
mark=`date +%Y%m%d%H%M`
time_out=20
status="ok"
check_status="Locked"
send_mail="off"
mysql_default_password="123456"
host_name=`hostname`

declare -a mysqllist
declare -a mysql_exec_path
declare -a mysql_password
declare -a mysql_locked_port
declare -a mysql_show_port

function usage(){
        cat << HELP

$0 -- USAGE: sh $0 mysql_exec_path mysql_password mysql_socket

Example: sh $0 /opt/phpdba/mysql/bin/mysql xxxxxxx /tmp/socket
HELP
}

function script_arg_init(){
	if [ "x$1" != "x0" ] ; then
		mysql_exec_path=$1
	else
		mysql_exec_path="/opt/phpdba/mysql/bin/mysql"
	fi

	if [ "x$2" != "x0" ];then
		mysql_password=$2
	else
		mysql_password="123456"
	fi

	if [ "x$3" != "x0" ];then
		mysql_socket=$3
	else
		mysql_socket="/tmy/mysql.sock"
	fi
	
	if [ "x$4" != "x" ];then
                mysql_locked_port=$4
        else
                mysql_locked_port=3306
        fi
}

function main(){
	script_arg_init $1 $2 $3 $4
	$mysql_exec_path -S $mysql_socket -p"$mysql_password" -e "show full processlist;"|grep -v "Id"|grep -v "show"|grep -v "system user"|grep "$check_status">log_monitor_$mysql_locked_port.txt 2>&1;
	OFF_SHELL=`cat log_monitor_${mysql_locked_port}.txt|awk ' ($6>'$time_out') && ($7=="'$check_status'"){printf "'$status'"}'`
	if [ -z $OFF_SHELL ];then
		echo "MySQL $mysql_locked_port is OK!"
		#exit 0
	else
		cat log_monitor_${mysql_locked_port}.txt |awk '($6>'$time_out') && ($7=="'$check_status'") {printf   $4" "$7" for "$6" seconds\nDetails:\n" $0"\n"}' > log_mail/log_mail_$mark.txt
		cat log_monitor_${mysql_locked_port}.txt |awk '($6>'$time_out') && ($7!="'$check_status'") {printf "\n\nOther details:\n" $0"\n"}' >> log_mail/log_mail_$mark.txt
		
		if [ "$send_mail"=="off" ];then
			send_mail="on"
		fi
		mysql_show_port=${mysql_locked_port}","$mysql_show_port
	fi
}

function mysqllist_get(){
        local mysqllist_get=`ps aux|grep mysql|grep 'socket'|sed 's/ /:/g'|awk '{print $0}'`

        export "$1"="$mysqllist_get"
}

mysqllist_get mysqllist

for i in $mysqllist;do
                for j in `echo $i|awk -F ':' '{ k=1;while(k<=NF){print $k;k++}}'`;do

                if [ -n "${j}" ] && ([ `echo $j|grep 'datadir='` ] || [ `echo $j|grep 'socket='` ] || [ `echo $j|grep 'port='` ]);then
                        #mysql_datastr=(`echo $j|awk -F "=" '{print $2}'`)
                        if [ `echo $j|grep 'datadir='` ];then
                                mysql_datadir=(`echo $j|awk -F "=" '{print $2}'`)
                        elif [ `echo $j|grep 'socket='` ];then
                                mysql_socket=(`echo $j|awk -F "=" '{print $2}'`)
                        elif [ `echo $j|grep 'port='` ];then
                                mysql_port=(`echo $j|awk -F "=" '{print $2}'`)
                        fi
                fi
                done
	
		if [ "x$mysql_port" != "x3316" ];then
			main 0 $mysql_default_password $mysql_socket $mysql_port
		else
			main 0 'xxxxx' $mysql_socket $mysql_port
		fi
done

if [ "$send_mail" == "on" ] ;then
	ip=`/bin/sh get_ip.sh|/usr/bin/head -n 1`
	email_content=`cat log_mail/log_mail_$mark.txt`
	mysql_show_email_port=`echo $mysql_show_port|cut -c1-$((${#mysql_show_port}-1))`
	sendEmail -s smtp.163.com -f alert@163.com -t alert@phpdba.com -a log_mail/log_mail_${mark}.txt -u "ALERT:${host_name}[${ip}] Locked Table ${mysql_show_email_port} " -m "${email_content}" -xu phpdba -xp phpdba
        echo "$mark send email"
fi
