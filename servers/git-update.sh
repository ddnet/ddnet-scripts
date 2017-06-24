#!/usr/bin/env zsh
set -e -x
rni 10 3

cd /home/teeworlds/servers
(set +x; ./config_store_d maps/*.map) > /dev/null 2>/dev/null
git commit -a -m "upd"
git push

(ni 12 3 nim-scripts/mapdl &
scripts/update-local.sh
#scripts/update-servers.sh
scripts/build-releasedates.sh
scripts/update-points.py `cat all-types`
scripts/releases.py > /var/www/releases/index.$$.tmp
mv /var/www/releases/index.$$.tmp /var/www/releases/index.html
scripts/releases-feed.py > /var/www/releases/feed/index.$$.tmp
mv /var/www/releases/feed/index.$$.tmp /var/www/releases/feed/index.atom
scripts/releases-all.py > /var/www/releases/all/index.$$.tmp
mv /var/www/releases/all/index.$$.tmp /var/www/releases/all/index.html
echo -e "\e[1;32mMAIN updated successfully\e[0m") &

for i in `cat all-locations`; do
  (ssh $i.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
  echo -e "\e[1;32m$i updated successfully\e[0m") &
done

wait
echo -e "\e[1;31mAll servers updated successfully\e[0m"
