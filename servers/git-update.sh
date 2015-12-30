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
echo -e "\e[1;32mFRA updated successfully\e[0m") &

(ssh ger.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mGER updated successfully\e[0m") &

#(ssh ger2.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
#echo -e "\e[1;32mGER2 updated successfully\e[0m") &

(ssh usa.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mUSA updated successfully\e[0m") &

(ssh can.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mCAN updated successfully\e[0m") &

(ssh rus.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mRUS updated successfully\e[0m") &

(ssh chn.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mCHN updated successfully\e[0m") &

(ssh chl.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mCHL updated successfully\e[0m") &

(ssh bra.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mBRA updated successfully\e[0m") &

(ssh zaf.ddnet.tw "ni 10 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mZAF updated successfully\e[0m") &

wait
echo -e "\e[1;31mAll servers updated successfully\e[0m"
