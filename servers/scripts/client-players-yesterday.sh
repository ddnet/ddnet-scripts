#!/bin/sh
cat /home/teeworlds/servers/versionsrv.log | grep "^\[`date --date='1 days ago' +%y-%m-%d`" | grep "version request by" | sed -e "s/.*by //" | sort | uniq | wc -l
