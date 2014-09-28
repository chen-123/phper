./multi_main.sh -c config.txt -l iplist.txt #开始执行，可查看result目录下的日志来分析是否执行成功

脚本如下：

mssh.exp 执行远程服务器命令expect脚本
mscp.exp 向远程服务器上传或下载文件expect脚本（rsync）
thread.sh 向一台服务器发起动作
multi_main.sh 批量执行，对每台调用thread.sh

2014-07-02 修改当用户名或者端口输错，脚本进入死循环的问题。
2014-07-03 修复通过密钥认证登录方式下，第一个expect循环等待超时，程序退出问题。
