#!/usr/bin/env zsh
# Set execution every minute in crontab
date1=$(date +"%s")
date2=$(date -d "2017-04-09 20:01 CEST" +"%s")
diff=$(($date2-$date1))

#if [ $(( ($diff / 60) % 60)) -eq 0 ]; then
#  echo "broadcast \"$(($diff / 3600)) more hours to get the best team time on Monster!\"" > /home/teeworlds/servers/servers/*fifo
#  sleep 7
#  echo "broadcast \"Brutal map Aviate by SickCunt & [A] Awesome at 20:00 CET!\"" > /home/teeworlds/servers/servers/*fifo
#  sleep 7
#  echo "broadcast \"Big Birthday Weekend Tournament, more info on DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
#fi

if [ $diff -lt 0 ]; then
  exit
elif [ $(($diff / 60)) -lt 10 ]; then
  echo "broadcast \"Dummy Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"Get on the Tournament servers, it will be great!\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"German livestream by Hallowed1986 running on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
elif [ $(($diff / 3600)) -lt 1 ]; then
  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
    echo "broadcast \"Dummy Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    #sleep 7
    #echo "broadcast \"There will be a German livestream by Hallowed1984\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 2 ]; then
  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
    echo "broadcast \"Dummy Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    #sleep 7
    #echo "broadcast \"Practice on the Tournament servers - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 3 ]; then
  if [ $(( ($diff / 60) % 30)) -eq 0 ]; then
    echo "broadcast \"Dummy Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    sleep 7
    echo "broadcast \"Practice on the Tournament servers - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
  echo "broadcast \"Dummy Tournament in $(($diff / 3600)) hours (20:00 CEST)\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"\"" > /home/teeworlds/servers/servers/*fifo
fi

#echo "broadcast \"Dummy Tournament on RayB's ZooDrag on Sunday at 20:00 CEST!\"" > /home/teeworlds/servers/servers/*fifo
#sleep 7
#echo "broadcast \"More info on DDNet.tw, see you on Sunday and have fun!\"" > /home/teeworlds/servers/servers/*fifo
