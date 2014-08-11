#!/usr/bin/env zsh
SERVER=$1
inotail -f servers/$SERVER.log  | grep --line-buffered "^\[.*\]\[server\]: ClientID=.* rcon='.*'$\|^\[.*\]\[Server\]: id=.*" | sed -u -e "s/.*id=\(.*\) .* name='\(.*\)' score=.*/name\t\1\t\2/" | sed -u -e "s/.*ClientID=\(.*\) rcon='\(.*\)'$/\1\t\2/" | scripts/tron.py $2 $3 > servers/$SERVER.fifo
