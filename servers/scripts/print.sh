#!/usr/bin/env zsh
# Set execution every minute in crontab
date1=$(date +"%s")
date2=$(date -d "2026-06-13 20:01 CEST" +"%s")
diff=$(($date2-$date1))

#if [ $diff -lt 0 ]; then
#  exit
#fi
#elif [ $(($diff / 60)) -lt 10 ]; then
#  echo "broadcast \"Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#elif [ $(($diff / 3600)) -lt 1 ]; then
#  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
#    echo "broadcast \"Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(($diff / 3600)) -lt 2 ]; then
#  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
#    echo "broadcast \"Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(($diff / 3600)) -lt 3 ]; then
#  if [ $(( ($diff / 60) % 30)) -eq 0 ]; then
#    echo "broadcast \"Brutal Tournament in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
#  echo "broadcast \"Brutal Tournament in $(($diff / 3600)) hours (20:00 CEST)\"" > /home/teeworlds/servers/servers/*fifo
#fi

#if [ "$(date +%-M)" -eq 1 ] && [ $(( $(date +%-H) % 2 )) -eq 0 ]; then
#  echo "broadcast \"DDNet Brutal Tournament on Saturday, 20:00 CEST!\"" > /home/teeworlds/servers/servers/*fifo
#  sleep 7
#  echo "broadcast \"TheRottingHalls! Only 2 player teams, best time after 3h wins!\"" > /home/teeworlds/servers/servers/*fifo
#fi
