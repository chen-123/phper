#!/bin/sh
#脚本自动通过数据库根目录下connect脚步，匹配密码
#处理了connect中包含特殊字符及引号问题
#统计数据库实例及关键配置
#link： blog.phpdba.com
#date：2014-07-20
#author: chen-123

mark=`date +%Y%m%d%H%M`
time_out=20
status="ok"
check_status="Locked"
send_mail="off"
mysql_default_password="123456"
host_name=`hostname`
script_dir=`pwd`
total_mysql_num=0

declare -a mysqllist
declare -a mysql_exec_path
declare -a mysql_password
declare -a mysql_locked_port
declare -a mysql_show_port

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

function mysqllist_get(){
        local mysqllist_get=`ps aux|grep mysql|grep 'socket'|sed 's/ /:/g'|awk '{print $0}'`

        export "$1"="$mysqllist_get"
}

mysqllist_get mysqllist

for i in $mysqllist;do
                let total_mysql_num+=1
                for j in `echo $i|awk -F ':' '{ k=1;while(k<=NF){print $k;k++}}'`;do

                if [ -n "${j}" ] && ([ `echo $j|grep 'datadir='` ] || [ `echo $j|grep 'socket='` ] || [ `echo $j|grep 'port='` ] || [ `echo $j|grep 'defaults-file='` ]);then
                        if [ `echo $j|grep 'datadir='` ];then
                                mysql_datadir=(`echo $j|awk -F "=" '{print $2}'`)
                        elif [ `echo $j|grep 'socket='` ];then
                                mysql_socket=(`echo $j|awk -F "=" '{print $2}'`)
                        elif [ `echo $j|grep 'port='` ];then
                                mysql_port=(`echo $j|awk -F "=" '{print $2}'`)
                        elif [ `echo $j|grep 'defaults-file='` ];then
                                defaults_file=(`echo $j|awk -F "=" '{print $2}'`)
                        fi
                fi
                done

                test -z $mysql_port && mysql_port=3306
                test -z $defaults_file && defaults_file='/etc/my.cnf'

                echo ""
                echo $mysql_datadir"==="$mysql_socket"==="$mysql_port"==="$defaults_file
                mysql_basedir=`dirname $mysql_datadir`
                test -n $mysql_basedir && cd $mysql_basedir && connect_filename=`ls -l *.sh |grep connect|grep -v grep|awk '{print $NF}'`
                test $connect_filename && password=`awk -F'-p' '/-p/{if($2 ~ /ts/){a=length($2);b=substr($2,2,(a-2))}else{b=$2};print b}' $mysql_basedir'/'$connect_filename`
                test -z $password && password=$mysql_default_password
                test -n $defaults_file && mysql_cnf=`cat $defaults_file|grep -E '(log|pid|datadir|max|buffer|cache|timeout|size)'|grep -v '^#'` #&& echo ${mysql_cnf//=/#}
                password=${password//[\'|\"]/}

                for tmp in ${mysql_cnf//[ |        |        ]=[ |        |        ]/=};do
                        echo $tmp
                done

                echo "数据库实例"
                #echo 0 $password $mysql_socket $mysql_port

                [ -f '/opt/phpdba/mysql/bin/mysql' ] && script_arg_init 0 $password $mysql_socket $mysql_port
                $mysql_exec_path -S $mysql_socket -p"$mysql_password" -e "show databases;"
                echo "数据库slave状态"
                $mysql_exec_path -S $mysql_socket -p"$mysql_password" -e "show slave status\G"|grep -E '(Master|Running)'
done

echo "总共"$total_mysql_num"个mysql实例"
