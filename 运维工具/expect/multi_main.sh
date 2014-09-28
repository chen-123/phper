#!/bin/bash

######################  proc defination  ########################
# ignore rule
ignore_init()
{
        # ignore password
        array_ignore_pwd_length=0
        if [ -f ./ignore_pwd ]; then
                while read IGNORE_PWD
                do
                        array_ignore_pwd[$array_ignore_pwd_length]=$IGNORE_PWD
                        let array_ignore_pwd_length=$array_ignore_pwd_length+1
                done < ./ignore_pwd
        fi

        # ignore ip address
        array_ignore_ip_length=0
        if [ -f ./ignore_ip ]; then
                while read IGNORE_IP
                do
                        array_ignore_ip[$array_ignore_ip_length]=$IGNORE_IP
                        let array_ignore_ip_length=$array_ignore_ip_length+1
                done < ./ignore_ip
        fi
}

show_version()
{
        echo "version: 1.1"
        echo "updated date: 2014-07-02"
}

show_usage()
{
        echo -e "`printf %-16s "Usage: $0"` [-h|--help]"
        echo -e "`printf %-16s ` [-v|-V|--version]"
        echo -e "`printf %-16s ` [-l|--iplist ... ]"
        echo -e "`printf %-16s ` [-c|--config ... ]"
        echo -e "`printf %-16s ` [-t|--sshtimeout ... ]"
        echo -e "`printf %-16s ` [-T|--fttimeout ... ]"
        echo -e "`printf %-16s ` [-L|--bwlimit ... ]"
        echo -e "`printf %-16s ` [-n|--ignore]"
        #echo "ignr_flag: 'ignr'-some ip will be ignored; otherwise-all ip will be handled"
}

TOOLDIR=/root/chen-123/batch_shell
cd $TOOLDIR

IPLIST="iplist.txt"                     # IP列表，格式为IP 端口 用户名 密码
CONFIG_FILE="config.txt"                # 命令列表和文件传送配置列表，关键字为com:::和file:::
IGNRFLAG="noignr"                       # 如果置为ignr，则脚本会进行忽略条件的判断
SSHTIMEOUT=100                          # 远程命令执行相关操作的超时设定，单位为秒
SCPTIMEOUT=2000                         # 文件传送相关操作的超时设定，单位为秒
BWLIMIT=1024                            # 文件传送的带宽限速，单位为kbit/s
[ ! -d "result" ] && mkdir result

# 入口参数分析
TEMP=`getopt -o hvVl:c:t:T:L:n --long help,version,iplist:,config:,sshtimeout:,fttimeout:,bwlimit:,ignore -- "$@" 2>/dev/null`

[ $? != 0 ] && echo -e "\033[31mERROR: unknown argument! \033[0m\n" && show_usage && exit 1

# 会将符合getopt参数规则的参数摆在前面，其他摆在后面，并在最后面添加--
eval set -- "$TEMP"

while :
do
        [ -z "$1" ] && break;
        case "$1" in
                -h|--help)
                        show_usage; exit 0
                        ;;
                -v|-V|--version)
                        show_version; exit 0
                        ;;
                -l|--iplist)
                        IPLIST=$2; shift 2
                        ;;
                -c|--config)
                        CONFIG_FILE=$2; shift 2
                        ;;
                -t|--sshtimeout)
                        SSHTIMEOUT=$2; shift 2
                        ;;
                -T|--fttimeout)
                        SCPTIMEOUT=$2; shift 2
                        ;;
                -L|--bwlimit)
                        BWLIMIT=$2; shift 2
                        ;;
                -n|--ignore)
                        IGNRFLAG="ignr"; shift
                        ;;
                --)
                        shift
                        ;;
                *)
                        echo -e "\033[31mERROR: unknown argument! \033[0m\n" && show_usage && exit 1
                        ;;
        esac
done

################  main  #######################
BEGINDATETIME=`date "+%F %T"`
[ ! -f $IPLIST ] && echo -e "\033[31mERROR: iplist \"$IPLIST\" not exists, please check! \033[0m\n" && exit 1

[ ! -f $CONFIG_FILE ] && echo -e "\033[31mERROR: config \"$CONFIG_FILE\" not exists, please check! \033[0m\n" && exit 1

IP_count=$(egrep -v '^#|^$' $IPLIST|wc -l)
IP_init=1
while [[ $IP_init -le $IP_count ]]
do
        egrep -v '^#|^$' $IPLIST | sed -n "$IP_init,$(expr $IP_init + 50)p" > $IPLIST.tmp #并发50

        IPSEQ=0

        while read IP PORT USER PASSWD PASSWD_2ND PASSWD_3RD PASSWD_4TH OTHERS
       # while read Line
        do
                [ -z "`echo $IP | grep -E '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|CNS'`" ] && continue
                #if [ "`python $TOOLDIR/ckssh.py $IP $PORT`" == 'no' ];then
                #        [ ! -e ipnologin.txt ] && > ipnologin.txt
                #        [ -z "`grep $IP ipnologin.txt | grep $(date +%F)`" ] && echo "`date +%F_%H%M` $IP" >> ipnologin.txt
                #        continue
                #fi

                let IPSEQ=$IPSEQ+1

                # 如果启用了忽略，则进入忽略流程
                if [ $IGNRFLAG == "ignr" ]; then
                        ignore_init
                        ignored_flag=0

                        i=0
                        while [ $i -lt $array_ignore_pwd_length ]
                        do
                                [ ${PASSWD}x == ${array_ignore_pwd[$i]}x ] && ignored_flag=1 && break
                                let i=$i+1
                        done

                        [ $ignored_flag -eq 1 ] && continue

                        j=0
                        while [ $j -lt $array_ignore_ip_length ]
                        do
                                [ ${IP}x == ${array_ignore_ip[$j]}x ] && ignored_flag=1 && break
                                let j=$j+1
                        done

                        [ $ignored_flag -eq 1 ] && continue
                fi

                ####### Try password from here ####
                #for PW in $PASSWD $PASSWD_2ND $PASSWD_3RD $PASSWD_4TH
                #do
                #        PASSWD_USE=$PW
                #        $TOOLDIR/ssh.exp $IP $USER $PW $PORT true $SSHTIMEOUT
                #        [ $? -eq 0 ] && PASSWD_USE=$PW && break
                #done
                PASSWD_USE=$PASSWD

                IPcode=$(echo "ibase=16;$(echo "$IP" | xxd -ps -u)"|bc|tr -d '\\'|tr -d '\n')
                Portcode=$(echo "ibase=16;$(echo "$PORT" | xxd -ps -u)"|bc|tr -d '\\'|tr -d '\n')
                #USER=$USER
                PWcode=$(echo "ibase=16;$(echo "$PASSWD_USE" | xxd -ps -u)"|bc|tr -d '\\'|tr -d '\n')
                Othercode=$(echo "ibase=16;$(echo "$OTHERS" | xxd -ps -u)"|bc|tr -d '\\'|tr -d '\n')
                #echo $IPcode $Portcode $USER $PWcode $CONFIG_FILE $SSHTIMEOUT $SCPTIMEOUT $BWLIMIT $Othercode
                ./thread.sh $IPcode $Portcode $USER $PWcode $CONFIG_FILE $SSHTIMEOUT $SCPTIMEOUT $BWLIMIT $Othercode | tee result/$IP.log &
        done < $IPLIST.tmp
        sleep 3
        IP_init=$(expr $IP_init + 50)
done

ENDDATETIME=`date "+%F %T"`

echo "$BEGINDATETIME -- $ENDDATETIME"
echo "$0 $* --excutes over!"

exit 0
