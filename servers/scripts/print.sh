#!/usr/bin/env zsh
# Set execution every minute in crontab
#date1=$(date +"%s")
#date2=$(date -d "2015-07-18 20:01 CEST" +"%s")
#diff=$(($date2-$date1))
#
#if [ $diff -lt 0 ]; then
#  exit
#elif [ $(($diff / 60)) -lt 10 ]; then
#  echo "broadcast \"Solo Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#  sleep 7
#  echo "broadcast \"Get on the Tournament servers, it will be great!\"" > /home/teeworlds/servers/servers/*fifo
#  sleep 7
#  echo "broadcast \"Livestream by Hallowed1986 running on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
#elif [ $(($diff / 3600)) -lt 1 ]; then
#  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
#    echo "broadcast \"Solo Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#    sleep 7
#    echo "broadcast \"Tournament servers running, more info on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
#    sleep 7
#    echo "broadcast \"There will be a livestream by Hallowed1986 on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(($diff / 3600)) -lt 2 ]; then
#  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
#    echo "broadcast \"Solo Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#    sleep 7
#    echo "broadcast \"Tournament servers are running already!\"" > /home/teeworlds/servers/servers/*fifo
#    sleep 7
#    echo "broadcast \"There will be a livestream by Hallowed1986 on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(($diff / 3600)) -lt 3 ]; then
#  if [ $(( ($diff / 60) % 30)) -eq 0 ]; then
#    echo "broadcast \"Solo Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#    sleep 7
#    echo "broadcast \"Tournament servers are running already!\"" > /home/teeworlds/servers/servers/*fifo
#    sleep 7
#    echo "broadcast \"There will be a livestream by Hallowed1986 on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
#  echo "broadcast \"Solo Tournament in $(($diff / 3600)) hours!\"" > /home/teeworlds/servers/servers/*fifo
#  sleep 6
#  echo "broadcast \"Everdeen by Themix - More info on DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
#  sleep 6
#  echo "broadcast \"There will be a livestream by Hallowed1986 on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
#fi

echo "broadcast \"DDNet turns 2 years old on Saturday!\"" > /home/teeworlds/servers/servers/*fifo
sleep 7
echo "broadcast \"Double Tournament this weekend - More info on DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
