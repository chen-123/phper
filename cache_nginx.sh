#! /bin/sh
#清除指定目录下，指定文件
#主要为了解决清除nginx缓存目录下的缓存文件
#link: blog.phpdba.com
#date: 2014-08-19
#author: chen-123

#Define Path
CACHE_DIR=/tmp/zaojiao.phpdba.com/
FILE="$*"

if [  "$#" -eq "0" ];then
        echo "Please Input clean File, Example: $0 index.html index.js style.css"
        sleep 2 && exit
fi
echo "The file : $FILE to be clean Cache ,please waiting ....."

for i in `echo $FILE`
do
        find ${CACHE_DIR} -name  $i > /tmp/cache_list.txt
        for j in `cat /tmp/cache_list.txt`
        do
                rm  -rf $j
                echo "$i $j is Deleted Success !"
        done
done
