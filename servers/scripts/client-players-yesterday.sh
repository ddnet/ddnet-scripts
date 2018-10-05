#!/bin/sh
cat /home/teeworlds/servers/versionsrv.log | grep -a "^\[`date --date='1 days ago' +%Y-%m-%d`" | grep "version request by" | sed -e "s/.*by //" | sort | uniq | wc -l
