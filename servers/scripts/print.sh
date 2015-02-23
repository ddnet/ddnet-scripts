#!/usr/bin/env zsh
# Set execution every minute in crontab
date1=$(date +"%s")
date2=$(date -d "2015-02-22 20:01 CET" +"%s")
diff=$(($date2-$date1))

if [ $diff -lt 0 ]; then
  exit
elif [ $(($diff / 60)) -lt 10 ]; then
  echo "broadcast \"Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  sleep 7
  echo "broadcast \"Get on the Tournament servers!\"" > /home/teeworlds/servers/servers/*fifo
elif [ $(($diff / 3600)) -lt 1 ]; then
  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
    echo "broadcast \"Easy Moderate Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    sleep 7
    echo "broadcast \"Everyone is invited! Come and have fun!\"" > /home/teeworlds/servers/servers/*fifo
    sleep 7
    echo "broadcast \"There will be an English livestream on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 2 ]; then
  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
    echo "broadcast \"Easy Moderate Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    sleep 7
    echo "broadcast \"Everyone is invited! Come and have fun!\"" > /home/teeworlds/servers/servers/*fifo
    sleep 7
    echo "broadcast \"There will be an English livestream on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 3 ]; then
  if [ $(( ($diff / 60) % 30)) -eq 0 ]; then
    echo "broadcast \"Easy Moderate Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    sleep 7
    echo "broadcast \"Everyone is invited! Come and have fun!\"" > /home/teeworlds/servers/servers/*fifo
    sleep 7
    echo "broadcast \"There will be an English livestream on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
  echo "broadcast \"Easy Moderate Tournament in $(($diff / 3600)) hours!\"" > /home/teeworlds/servers/servers/*fifo
  sleep 4
  echo "broadcast \"Tournament servers are running already!\"" > /home/teeworlds/servers/servers/*fifo
fi

#echo "broadcast \"Easy Moderate Tournament on Sunday, 20:00 CET!\"" > /home/teeworlds/servers/servers/*fifo
#sleep 7
#echo "broadcast \"Jvice by Vasten100, 60 minutes for best time - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
