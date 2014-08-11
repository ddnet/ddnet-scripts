#!/usr/bin/env zsh
# Set execution every minute in crontab
date1=$(date +"%s")
date2=$(date -d "2014-08-10 19:01 CEST" +"%s")
diff=$(($date2-$date1))

if [ $diff -lt 0 ]; then
  exit
elif [ $(($diff / 60)) -lt 10 ]; then
  echo "broadcast \"DDNet Moderate Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  sleep 7
  echo "broadcast \"Get on the Tournament servers!\"" > /home/teeworlds/servers/servers/*fifo
elif [ $(($diff / 3600)) -lt 1 ]; then
  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
    echo "broadcast \"DDNet Moderate Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 2 ]; then
  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
    echo "broadcast \"DDNet Moderate Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
  echo "broadcast \"DDNet Moderate Tournament in $(($diff / 3600)) hours!\"" > /home/teeworlds/servers/servers/*fifo
  sleep 7
  echo "broadcast \"New map by Bixes & Themix! More info on ddnet.tw\"" > /home/teeworlds/servers/servers/*fifo
fi

#echo "broadcast \"DDNet Moderate Tournament on Sunday, 19:00 CEST!\"" > /home/teeworlds/servers/servers/*fifo
#sleep 7
#echo "broadcast \"New map by Bixes & Themix! More info on ddnet.tw\"" > /home/teeworlds/servers/servers/*fifo
