#!/bin/bash

ps -ef |grep -i -E "mtopctl|mtopdv2.1.py"|grep -v -E "vi|grep"|awk '{print $2}' |while read line; do kill $line; echo "mtop processes id $line been stop"; done
