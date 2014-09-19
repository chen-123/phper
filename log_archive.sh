#!/bin/sh
#将当前目录下常规apache日志文件，按照月份归集
#link： blog.phpdba.com
#date：2014-07-29
#author: chen-123

export LANG="en_US.UTF-8"
project_list=`ls -l|grep 'access\.'|awk '{print $NF}'|awk -F'-access.' '{print $1}'|uniq`
month_list=`ls -l|grep 'access\.'|awk '{print $NF}'|awk -F'-access.' '{print $2}'|sort -n|uniq|cut -c 1-2|uniq`
cur_month=`date +%m`
for project in $project_list
do
for month in $month_list
do
echo $project
log_num=`ls |grep $project'-access.'$month|wc -l`
echo $log_num
if [ $log_num -gt 0 ];then
        if [ "$month" != "$cur_month" ];then
                echo $project" "$month" "$log_num
                tar_file=${project}"_access_"${month}".tar.gz"
                files=${project}"-access."${month}"[0-9][0-9]"
                files_total_size=`ls $files|xargs du -cb|grep total|awk '{print $1}'`
                files_avg_size=`echo "$files_total_size/$log_num"|bc`
                echo $files_avg_size
                if [ $files_avg_size -gt 1073741824 ];then
                        for file in $files
                        do
                                day=`echo $file|awk -F'-access.' '{print $2}'`
                                tar_filenew=${project}"_access_"${day}".tar.gz"
                                echo $tar_filenew
                                [ -f $tar_filenew ] || /bin/tar zcf $tar_filenew $file
                                [ -f $tar_filenew ] && rm -f $file
                        done
                else
                        echo $tar_file
                        [ -f $tar_file ] || /bin/tar zcf $tar_file $files
                        [ -f $tar_file ] && rm -f $files
                fi
                #echo $files_total_size
                #/bin/tar zcf $tar_file $files
        fi
fi
done
done
