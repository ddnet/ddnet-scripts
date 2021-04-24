#!/usr/bin/env zsh
# Set execution every minute in crontab
date1=$(date +"%s")
date2=$(date -d "2021-04-25 20:01 CEST" +"%s")
diff=$(($date2-$date1))

if [ $diff -lt 0 ]; then
  exit
elif [ $(($diff / 60)) -lt 10 ]; then
  echo "broadcast \"3-player Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"Get on the Tournament servers, it will be great!\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"German livestream by Hallowed1986 running on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
elif [ $(($diff / 3600)) -lt 1 ]; then
  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
    echo "broadcast \"3-player Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    #sleep 7
    #echo "broadcast \"There will be a German livestream by Hallowed1984\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 2 ]; then
  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
    echo "broadcast \"3-player Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    #sleep 7
    #echo "broadcast \"Tournament servers running already - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 3 ]; then
  if [ $(( ($diff / 60) % 30)) -eq 0 ]; then
    echo "broadcast \"3-player Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    #sleep 7
    #echo "broadcast \"Tournament servers running already - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
  echo "broadcast \"3-player Brutal Tournament in $(($diff / 3600)) hours (20:00 CEST)\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"\"" > /home/teeworlds/servers/servers/*fifo
fi

#echo "broadcast \"3-player Brutal Tournament on Sunday, 20:00 CEST!\"" > /home/teeworlds/servers/servers/*fifo
#sleep 7
#echo "broadcast \"Map by Tridemy & Cøke, first finish wins\"" > /home/teeworlds/servers/servers/*fifo
