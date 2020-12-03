#!/bin/sh
grep -a "^\[$(date +%Y-%m-%d)" /home/teeworlds/servers/versionsrv.log | \
    grep "version request by" | \
    sed -e "s/.*by //" | \
    sort | uniq | wc -l

