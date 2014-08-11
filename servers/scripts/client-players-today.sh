#!/bin/sh
cat /home/teeworlds/servers/versionsrv.log | grep "^\[`date +%y-%m-%d`" | grep "version request by" | sed -e "s/.*by //" | sort | uniq | wc -l
