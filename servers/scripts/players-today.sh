#!/bin/sh
cat /home/teeworlds/servers/servers/*log* | grep "^\[`date +%y-%m-%d`" | grep "player has entered the game" | sed -e "s/.*addr=\(.*\):.*/\1/" | sort | uniq | wc -l
