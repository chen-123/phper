#/bin/sh
# 脚本用于批量删除指定目录下小文件
# link：blog.phpdba.com
# date: 2014-08-18
# author: chen-123

Base_Folder="/ask_d"
Folder='askques'
Old_Folder='askques_old'
Tmp_Folder='tmp'
Check_Old="yes"



if [ "`pwd`" != "$Base_Folder" ]
then
        echo "请将脚本放在"$Base_Folder"目录下执行"
        exit
fi


if [ -d $Tmp_Folder -a "`ls -A $Tmp_Folder`" != "" ]
then
        echo "请检查目录"$Tmp_Folder"是否为空目录"
fi

if [ -d $Old_Folder ]
then
        echo "目录存在"
        if [ "`ls -A $Old_Folder`" == "" ];then
                echo "$Old_Folder 是空目录，请重新执行一次"
                `rm -rf $Old_Folder`
        else
                Old_Size=`du -s ${Old_Folder}|awk '{print $1}'`

                if [ $Old_Size -ge 102400 ]
                then
                        echo $Old_Folder"目录比较大，请检查"
                        if [ "$Check_Old" != "yes" ]
                        then
                                if [ -d $Tmp_Folder ]
                                then
                                        rsync --delete-before -a -H -v --progress --stats $Base_Folder"/"$Tmp_Folder"/" $Base_Folder"/"$Old_Folder"/"
                                else
                                        echo "请确认"$Tmp_Folder"目录是否存在"
                                fi
                        fi
                else
                        echo "正在删除目录"$Old_Folder" ,请重新执行一次"
                        `rm -rf $Old_Folder`
                fi
        fi
else
        echo "目录不存在,创建目录"$Old_Folder
        `mv $Folder $Old_Folder && mkdir $Folder && chown -R apache:apache $Folder`
        if [ -d $Tmp_Folder ]
        then
                rsync --delete-before -a -H -v --progress --stats $Base_Folder"/"$Tmp_Folder"/" $Base_Folder"/"$Old_Folder"/"
                `rm -rf $Old_Folder`
        else
                echo "请确认"$Tmp_Folder"目录是否存在"
        fi
fi
