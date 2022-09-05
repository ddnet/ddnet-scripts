#!/bin/sh
# crontab entry:
# */2   * * * * /home/deen/ddnetstatus/down.sh
mkdir -p ~/ddnetstatus
cd ~/ddnetstatus || exit
FILE=$(date +status.%Y-%m-%d.%H-%M).html
wget -q -O "$FILE" https://ddnet.tw/status/
NUM=$(grep "DDraceNetwork Status:" "$FILE" | sed -e "s/.*DDraceNetwork Status: \([0-9]*\) players.*/\1/")
if [ "$NUM" -lt 4000 ]; then
  rm -- "$FILE"
fi
