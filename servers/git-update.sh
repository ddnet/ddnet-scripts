#!/usr/bin/env zsh
set -e -x

cd /home/teeworlds/servers
nice -n 19 ionice -c 3 git commit -a -m "upd"
nice -n 19 ionice -c 3 git push

(nice -n19 ionice -c3 nim-scripts/mapdl
nice -n 19 ionice -c 3 scripts/update-local.sh
#nice -n 19 ionice -c 3 scripts/update-servers.sh
nice -n 19 ionice -c 3 scripts/update-points.py `cat all-types`
nice -n 19 ionice -c 3 scripts/build-releasedates.sh
nice -n19 ionice -c3 scripts/releases.py > /var/www/releases/index.tmp
mv /var/www/releases/index.tmp /var/www/releases/index.html
nice -n19 ionice -c3 scripts/releases-all.py > /var/www/releases/all/index.tmp
mv /var/www/releases/all/index.tmp /var/www/releases/all/index.html
echo -e "\e[1;32mFRA updated successfully\e[0m") &

(ssh ger.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mGER updated successfully\e[0m") &

(ssh ger2.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mGER2 updated successfully\e[0m") &

(ssh usa.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mUSA updated successfully\e[0m") &

(ssh can.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mCAN updated successfully\e[0m") &

(ssh rus.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mRUS updated successfully\e[0m") &

(ssh chn.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mCHN updated successfully\e[0m") &

(ssh chl.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mCHL updated successfully\e[0m") &

(ssh bra.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mBRA updated successfully\e[0m") &

(ssh zaf.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mZAF updated successfully\e[0m") &
