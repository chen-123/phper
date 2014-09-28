#!/bin/bash

# Default Parameters
myIFS=":::"     # 配置文件中的分隔符
TOOLDIR=/root/chen-123/batch_shell
cd $TOOLDIR

#BEGINDATETIME=`date "+%F %T"`

IP=$1P
PORT=$2P
USER=$3
PASSWD=$4P
CONFIG_FILE=$5                # 命令列表和文件传送配置列表，关键字为com:::和file:::
SSHTIMEOUT=$6                 # 远程命令执行相关操作的超时设定，单位为秒
SCPTIMEOUT=$7                 # 文件传送相关操作的超时设定，单位为秒
BWLIMIT=$8                    # 文件传送的带宽限速，单位为kbit/s

# 针对一个$IP，执行配置文件中的一整套操作
while read eachline
do
        # 必须以com或file开头
        [ -z "`echo $eachline | grep -E '^com|^file'`" ] && continue

        myKEYWORD=`echo $eachline | awk -F"$myIFS" '{ print $1 }'`
        myCONFIGLINE=`echo $eachline | awk -F"$myIFS" '{ print $2 }'`

        # 配置文件中有关键字file:::，就调用mscp.exp进行文件传送
        if [ "$myKEYWORD"x == "file"x ]; then
                SOURCEFILE=`echo $myCONFIGLINE | awk '{ print $1 }'`
                DESTDIR=`echo $myCONFIGLINE | awk '{ print $2 }'`
                DIRECTION=`echo $myCONFIGLINE | awk '{ print $3 }'`
                $TOOLDIR/mscp.exp $IP $USER $PASSWD $PORT $SOURCEFILE $DESTDIR $DIRECTION $BWLIMIT $SCPTIMEOUT

                [ $? -ne 0 ] && echo -e "\033[31mSCP Try Out All Password Failed\033[0m\n"

        # 配置文件中有关键字com:::，就调用mssh.exp进行远程命令执行
        elif [ "$myKEYWORD"x == "com"x ]; then
		#echo $IP $USER $PASSWD $PORT "${myCONFIGLINE}" $SSHTIMEOUT
                $TOOLDIR/mssh.exp $IP $USER $PASSWD $PORT "${myCONFIGLINE}" $SSHTIMEOUT
                #echo  $IP $USER $PASSWD $PORT "${myCONFIGLINE}" $SSHTIMEOUT
                [ $? -ne 0 ] && echo -e "\033[31mSSH Try Out All Password Failed\033[0m\n"

        else
                echo "ERROR: configuration wrong! [$eachline] "
                echo "       where KEYWORD should not be [$myKEYWORD], but 'com' or 'file'"
                echo "       if you dont want to run it, you can comment it with '#'"
                echo ""
                exit
        fi

done < $CONFIG_FILE

#ENDDATETIME=`date "+%F %T"`

#echo "$BEGINDATETIME -- $ENDDATETIME"
#echo "$0 $* --excutes over!"

exit 0
