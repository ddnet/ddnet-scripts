#!/usr/bin/env zsh
set -e -x
rni 10 3

cd /home/teeworlds/servers

(scripts/shutdown-empty.sh
echo -e "\e[1;32mFRA servers restart when empty\e[0m") &

(ssh ger.ddnet.org "ni 10 3 servers/scripts/shutdown-empty.sh"
echo -e "\e[1;32mGER servers restart when empty\e[0m") &

(ssh ger2.ddnet.org "ni 10 3 servers/scripts/shutdown-empty.sh"
echo -e "\e[1;32mGER2 servers restart when empty\e[0m") &

(ssh usa.ddnet.org "ni 10 3 servers/scripts/shutdown-empty.sh"
echo -e "\e[1;32mUSA servers restart when empty\e[0m") &

(ssh can.ddnet.org "ni 10 3 servers/scripts/shutdown-empty.sh"
echo -e "\e[1;32mCAN servers restart when empty\e[0m") &

(ssh rus.ddnet.org "ni 10 3 servers/scripts/shutdown-empty.sh"
echo -e "\e[1;32mRUS servers restart when empty\e[0m") &

(ssh chn.ddnet.org "ni 10 3 servers/scripts/shutdown-empty.sh"
echo -e "\e[1;32mCHN servers restart when empty\e[0m") &

(ssh chl.ddnet.org "ni 10 3 servers/scripts/shutdown-empty.sh"
echo -e "\e[1;32mCHL servers restart when empty\e[0m") &

(ssh bra.ddnet.org "ni 10 3 servers/scripts/shutdown-empty.sh"
echo -e "\e[1;32mBRA servers restart when empty\e[0m") &

(ssh zaf.ddnet.org "ni 10 3 servers/scripts/shutdown-empty.sh"
echo -e "\e[1;32mZAF servers restart when empty\e[0m") &

wait
echo -e "\e[1;31mAll servers restart when empty\e[0m"
