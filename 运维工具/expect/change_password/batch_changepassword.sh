#!/bin/sh
cat /root/chen-123/expect/change_password/$1|while read line
do
   echo $line
   /usr/bin/expect batch_changepassword.exp $line $2
   sleep 3
done 
