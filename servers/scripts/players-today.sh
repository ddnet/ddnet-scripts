#!/bin/sh

cat /home/teeworlds/servers/servers/*log* | \
    grep -a "^\[$(date +%Y-%m-%d)" | \
    grep "player has entered the game" | \
    sed -e "s/.*addr=\(.*\):.*/\1/" | \
    sort | uniq | wc -l

