#!/bin/sh
cd /home/teeworlds/servers
sleep 428m
mv ../*.map maps/
git add maps/Pharice\ 2.map
git add maps/Wormhole.map
./git-update-files-only.sh
for i in ger fra rus chl zaf usa can chn; do
  ssh $i "servers/tournament-start.sh" &
done
