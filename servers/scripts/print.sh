#!/usr/bin/env zsh
# Set execution every minute in crontab
date1=$(date +"%s")
date2=$(date -d "2022-03-13 18:01 CET" +"%s")
diff=$(($date2-$date1))

if [ $diff -lt 0 ]; then
  exit
elif [ $(($diff / 60)) -lt 10 ]; then
  echo "broadcast \"Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"Get on the Tournament servers, it will be great!\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"German livestream by Hallowed1986 running on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
elif [ $(($diff / 3600)) -lt 1 ]; then
  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
    echo "broadcast \"Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    #sleep 7
    #echo "broadcast \"There will be a German livestream by Hallowed1984\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 2 ]; then
  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
    echo "broadcast \"Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    #sleep 7
    #echo "broadcast \"Tournament servers running already - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 3 ]; then
  if [ $(( ($diff / 60) % 30)) -eq 0 ]; then
    echo "broadcast \"Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    #sleep 7
    #echo "broadcast \"Tournament servers running already - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
  echo "broadcast \"Brutal Tournament in $(($diff / 3600)) hours (18:00 CET)\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"\"" > /home/teeworlds/servers/servers/*fifo
fi

#echo "broadcast \"DDNet Brutal Tournament on Sunday, 18:00 CET!\"" > /home/teeworlds/servers/servers/*fifo
#sleep 7
#echo "broadcast \"Map Simple Down by Zweitleben, first finish wins!\"" > /home/teeworlds/servers/servers/*fifo
