#!/bin/sh

grep -a "^\[$(date --date='1 days ago' +%y-%m-%d)" /home/teeworlds/servers/versionsrv.log | \
    grep "version request by" | \
    sed -e "s/.*by //" | \
    sort | \
    uniq | while read -r line; \
    do
        geoiplookup "$line";
    done | sort | uniq -c | sort -gr

