#!/usr/bin/env zsh
# Set execution every minute in crontab
date1=$(date +"%s")
date2=$(date -d "2014-09-28 20:01 CEST" +"%s")
diff=$(($date2-$date1))

if [ $diff -lt 0 ]; then
  exit
elif [ $(($diff / 60)) -lt 10 ]; then
  echo "broadcast \"Kobra 3 Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  sleep 7
  echo "broadcast \"Get on the Tournament servers!\"" > /home/teeworlds/servers/servers/*fifo
elif [ $(($diff / 3600)) -lt 1 ]; then
  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
    echo "broadcast \"Kobra 3 Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    sleep 7
    echo "broadcast \"There will be a German livestream on ddnet.tw!\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(($diff / 3600)) -lt 2 ]; then
  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
    echo "broadcast \"Kobra 3 Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  fi
elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
  echo "broadcast \"Kobra 3 Tournament in $(($diff / 3600)) hours!\"" > /home/teeworlds/servers/servers/*fifo
  sleep 7
  echo "broadcast \"Before we will see Saavik's great loading screen\"" > /home/teeworlds/servers/servers/*fifo
fi

#echo "broadcast \"Kobra 3 Tournament on Sunday, 20:00 CEST!\"" > /home/teeworlds/servers/servers/*fifo
#sleep 7
#echo "broadcast \"Finally a new Kobra by Zerodin! More info on ddnet.tw\"" > /home/teeworlds/servers/servers/*fifo
