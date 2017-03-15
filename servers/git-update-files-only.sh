#!/usr/bin/env zsh
set -e -x
rni 10 3

cd /home/teeworlds/servers
(set +x; ./config_store_d maps/*.map) > /dev/null 2>/dev/null
git commit -a -m "upd"
git push
echo -e "\e[1;32mMAIN updated successfully\e[0m"

nohup nim-scripts/mapdl &

for i in `cat all-locations`; do
  (ssh $i.ddnet.tw "cd servers;ni 10 3 git pull"
  echo -e "\e[1;32m$i updated successfully\e[0m") &
done

wait
echo -e "\e[1;31mAll servers updated successfully\e[0m"
