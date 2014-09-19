#!/bin/sh
OS=`uname`
IO="" 
case $OS in
Linux) IP=`/sbin/ifconfig  | grep 'inet addr:'| grep -v -E '127.0.0.1|192.168.' | cut -d: -f2 | awk '{ print $1}'`;;
FreeBSD|OpenBSD) IP=`ifconfig  | grep -E 'inet.[0-9]' | grep -v -E '127.0.0.1|192.168.' | awk '{ print $2}'` ;;
SunOS) IP=`ifconfig -a | grep inet | grep -v -E '127.0.0.1|192.168.' | awk '{ print $2} '` ;;
*) IP="Unknown";;
esac
echo "$IP"
