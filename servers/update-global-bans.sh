#!/usr/bin/env zsh
set -e -x
rni 10 3

cd /home/teeworlds/servers

git add bans.cfg
git commit -m "upd"
git push

(ssh ger.ddnet.tw "cd servers;ni 10 3 git pull; scripts/update-bans.sh"
echo -e "\e[1;32mGER bans updated successfully\e[0m") &

#(ssh ger2.ddnet.tw "cd servers;ni 10 3 git pull; scripts/update-bans.sh"
#echo -e "\e[1;32mGER2 bans updated successfully\e[0m") &

(ssh usa.ddnet.tw "cd servers;ni 10 3 git pull; scripts/update-bans.sh"
echo -e "\e[1;32mUSA bans updated successfully\e[0m") &

(ssh can.ddnet.tw "cd servers;ni 10 3 git pull; scripts/update-bans.sh"
echo -e "\e[1;32mCAN bans updated successfully\e[0m") &

(ssh rus.ddnet.tw "cd servers;ni 10 3 git pull; scripts/update-bans.sh"
echo -e "\e[1;32mRUS bans updated successfully\e[0m") &

(ssh chn.ddnet.tw "cd servers;ni 10 3 git pull; scripts/update-bans.sh"
echo -e "\e[1;32mCHN bans updated successfully\e[0m") &

(ssh chl.ddnet.tw "cd servers;ni 10 3 git pull; scripts/update-bans.sh"
echo -e "\e[1;32mCHL bans updated successfully\e[0m") &

(ssh bra.ddnet.tw "cd servers;ni 10 3 git pull; scripts/update-bans.sh"
echo -e "\e[1;32mBRA bans updated successfully\e[0m") &

(ssh zaf.ddnet.tw "cd servers;ni 10 3 git pull; scripts/update-bans.sh"
echo -e "\e[1;32mZAF bans updated successfully\e[0m") &
