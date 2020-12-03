#!/bin/sh

grep -a "^\[$(date --date='1 days ago' +%Y-%m-%d)" /home/teeworlds/servers/versionsrv.log | \
    grep "version request by" | \
    sed -e "s/.*by //" | \
    sort | uniq | wc -l

