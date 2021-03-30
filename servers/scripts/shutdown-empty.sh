#!/usr/bin/env zsh
find /home/teeworlds/servers/servers /home/teeworlds/servers7/servers /home/teeworlds/zcatch-configs/fifos /home/teeworlds/blockz/servers -name '*.fifo' 2> /dev/null | while read line; do
  echo sv_shutdown_when_empty 1 > $line
done
