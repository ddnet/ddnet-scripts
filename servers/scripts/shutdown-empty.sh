#!/usr/bin/env zsh
setopt extendedglob
echo sv_shutdown_when_empty 1 > /home/teeworlds/servers/servers/*.fifo
test -d /home/teeworlds/servers7/servers && echo sv_shutdown_when_empty 1 > /home/teeworlds/servers7/servers/*.fifo
test -d /home/teeworlds/zcatch-configs/fifos && echo sv_shutdown_when_empty 1 > /home/teeworlds/zcatch-configs/fifos/*.fifo
test -d /home/teeworlds/blockz/servers && echo sv_shutdown_when_empty 1 > /home/teeworlds/blockz/servers/*.fifo
