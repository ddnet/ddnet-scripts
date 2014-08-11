#!/usr/bin/env zsh
set -e -x

cd /home/teeworlds/servers
nice -n 19 ionice -c 3 git commit -a -m "upd"
nice -n 19 ionice -c 3 git push

(nice -n 19 ionice -c 3 scripts/update-local.sh
nice -n 19 ionice -c 3 scripts/update-servers.sh
nice -n 19 ionice -c 3 scripts/update-points.py `cat all-types`
echo -e "\e[1;32mGER updated successfully\e[0m") &

(ssh usa.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mUSA updated successfully\e[0m") &

(ssh rus.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mRUS updated successfully\e[0m") &

(ssh irn.ddnet.tw "nice -n 19 ionice -c 2 servers/scripts/git-remote.sh"
echo -e "\e[1;32mIRN updated successfully\e[0m") &

(ssh chn.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mCHN updated successfully\e[0m") &

(ssh chl.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mCHL updated successfully\e[0m") &

(ssh zaf.ddnet.tw "nice -n 19 ionice -c 3 servers/scripts/git-remote.sh"
echo -e "\e[1;32mZAF updated successfully\e[0m") &
