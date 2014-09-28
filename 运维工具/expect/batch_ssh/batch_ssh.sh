#!/bin/sh
cat /root/chen-123/expect/batch_ssh/$1|while read line
do
   cat /root/chen-123/expect/batch_ssh/$1|while read line2
   do
   if [ $line != $line2 ];then
   echo "line:${line}--line2:{$line2}"
   /usr/bin/expect batch_ssh.exp $line $2 $line2 $2
   fi
   sleep 1
   done
done
