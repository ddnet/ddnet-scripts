#!/bin/sh
cat /home/teeworlds/servers/versionsrv.log | grep -a "^\[`date +%y-%m-%d`" | grep "version request by" | sed -e "s/.*by //" | sort | uniq | while read line; do geoiplookup $line; done | sort | uniq -c | sort -gr
