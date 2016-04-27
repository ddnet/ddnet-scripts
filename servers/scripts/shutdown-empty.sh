#!/usr/bin/env zsh
echo sv_shutdown_when_empty 1 > /home/teeworlds/servers/servers/*.fifo
test -d /home/teeworlds/zcatch-configs/fifos && echo sv_shutdown_when_empty 1 > /home/teeworlds/zcatch-configs/fifos/*.fifo
