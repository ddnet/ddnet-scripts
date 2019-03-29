#!/usr/bin/env zsh
set -x
rni 10 3

cd /home/teeworlds/servers
(set +x; ./config_store_d maps/*.map) > /dev/null 2>/dev/null
git commit -a -m "upd"
git push
echo -e "\e[1;32mMAIN updated successfully\e[0m"

nohup nim-scripts/mapdl &

servers=0
for i in `cat all-locations`; do
  ssh $i.ddnet.tw "cd servers;ni 10 3 git pull"
  if [ $? -eq 0 ]; then
    echo -e "\e[1;32m$i updated successfully\e[0m"
    servers=$((servers+1))
  else
    echo -e "\e[1;33mUpdating $i failed\e[0m"
  fi
done

wait
echo -e "\e[1;31m$servers/$(wc -w < all-locations) servers updated successfully\e[0m"
