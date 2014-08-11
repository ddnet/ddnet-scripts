#!/usr/bin/env zsh
set -e -x

cd /home/teeworlds/servers
nice -n 19 ionice -c 3 git commit -a -m "upd"
nice -n 19 ionice -c 3 git push
echo -e "\e[1;32mGER updated successfully\e[0m"

(ssh usa.ddnet.tw "cd servers;nice -n 19 ionice -c 3 git pull"
echo -e "\e[1;32mUSA updated successfully\e[0m") &

(ssh rus.ddnet.tw "cd servers;nice -n 19 ionice -c 3 git pull"
echo -e "\e[1;32mRUS updated successfully\e[0m") &

(ssh irn.ddnet.tw "cd servers;nice -n 19 ionice -c 2 git pull"
echo -e "\e[1;32mIRN updated successfully\e[0m") &

(ssh chn.ddnet.tw "cd servers;nice -n 19 ionice -c 3 git pull"
echo -e "\e[1;32mCHN updated successfully\e[0m") &

(ssh chl.ddnet.tw "cd servers;nice -n 19 ionice -c 3 git pull"
echo -e "\e[1;32mCHL updated successfully\e[0m") &

(ssh zaf.ddnet.tw "cd servers;nice -n 19 ionice -c 3 git pull"
echo -e "\e[1;32mZAF updated successfully\e[0m") &
