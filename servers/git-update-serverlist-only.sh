#!/usr/bin/env zsh
rni 10 3
set -x

cd /home/teeworlds/servers
jq . serverlist.json > /dev/null || (echo "Invalid serverlist.json" && exit 1)
git commit -a -m upd
git push
ssh db.ddnet.org "cd servers && git pull || git pull"
