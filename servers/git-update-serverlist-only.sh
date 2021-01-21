#!/usr/bin/env zsh
rni 10 3
set -x

cd /home/teeworlds/servers
git commit -a -m upd
git push
ssh db.ddnet.tw "cd servers && git pull || git pull"
