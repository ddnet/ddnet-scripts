#!/usr/bin/env zsh
# Set execution every minute in crontab
date1=$(date +"%s")
date2=$(date -d "2017-08-07 20:01 CEST" +"%s")
diff=$(($date2-$date1))

#if [ $(( ($diff / 60) % 60)) -eq 0 ]; then
#  echo "broadcast \"Moderate map Tropica by jao & Shishigami at 20:00 CEST!\"" > /home/teeworlds/servers/servers/*fifo
#  sleep 7
#  echo "broadcast \"Big Birthday Weekend Tournament, more info on DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
#fi

#if [ $diff -lt 0 ]; then
#  exit
#elif [ $(($diff / 60)) -lt 10 ]; then
#  echo "broadcast \"Tournament on brainduck by ٭ıƞdex'<3 & Rapture in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#  #sleep 7
#  #echo "broadcast \"Get on the Tournament servers, it will be great!\"" > /home/teeworlds/servers/servers/*fifo
#  #sleep 7
#  #echo "broadcast \"German livestream by Hallowed1986 running on DDNet.tw!\"" > /home/teeworlds/servers/servers/*fifo
#elif [ $(($diff / 3600)) -lt 1 ]; then
#  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
#    echo "broadcast \"Tournament on brainduck by ٭ıƞdex'<3 & Rapture in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#    #sleep 7
#    #echo "broadcast \"There will be a German livestream by Hallowed1984\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(($diff / 3600)) -lt 2 ]; then
#  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
#    echo "broadcast \"Tournament on brainduck by ٭ıƞdex'<3 & Rapture in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#    #sleep 7
#    #echo "broadcast \"Tournament servers running already - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(($diff / 3600)) -lt 3 ]; then
#  if [ $(( ($diff / 60) % 30)) -eq 0 ]; then
#    echo "broadcast \"Tournament on brainduck by ٭ıƞdex'<3 & Rapture in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#    #sleep 7
#    #echo "broadcast \"Tournament servers running already - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
#  echo "broadcast \"Tournament on brainduck by ٭ıƞdex'<3 & Rapture in $(($diff / 3600)) hours (20:00 CEST)\"" > /home/teeworlds/servers/servers/*fifo
#  #sleep 7
#  #echo "broadcast \"\"" > /home/teeworlds/servers/servers/*fifo
#fi

if [ $diff -lt 0 ]; then
  exit
elif [ $(($diff / 60)) -lt 10 ]; then
  echo "broadcast \"DDNet Long Tournament ends in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
  #sleep 7
  #echo "broadcast \"Hermit by »Rogue. - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
elif [ $(($diff / 3600)) -lt 1 ]; then
  if [ $(( ($diff / 60) % 10)) -eq 0 ]; then
    echo "broadcast \"DDNet Long Tournament ends in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
    #sleep 7
    #echo "broadcast \"Hermit by »Rogue. - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
  fi
fi

#if [ $diff -lt 0 ]; then
#  exit
#elif [ $(($diff / 3600)) -lt 2 ]; then
#  if [ $(( ($diff / 60) % 20)) -eq 0 ]; then
#    echo "broadcast \"Last DDNet Long Tournament ends in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#    sleep 7
#    echo "broadcast \"HighLife by Skeptar & ٭ıƞdex'<3 on Brutal - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(($diff / 3600)) -lt 3 ]; then
#  if [ $(( ($diff / 60) % 30)) -eq 0 ]; then
#    echo "broadcast \"Last DDNet Long Tournament ends in $(($diff / 60)) minutes!\"" > /home/teeworlds/servers/servers/*fifo
#    sleep 7
#    echo "broadcast \"HighLife by Skeptar & ٭ıƞdex'<3 on Brutal - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
#  fi
#elif [ $(( ($diff / 60) % 60)) -eq 0 ]; then
#  echo "broadcast \"Last DDNet Long Tournament ends in $(($diff / 3600)) hours (20:00 CEST)\"" > /home/teeworlds/servers/servers/*fifo
#  sleep 7
#  echo "broadcast \"HighLife by Skeptar & ٭ıƞdex'<3 on Brutal - DDNet.tw\"" > /home/teeworlds/servers/servers/*fifo
#fi

#echo "broadcast \"Last DDNet Birthday Tournament on Sunday at 20:00 CEST!\"" > /home/teeworlds/servers/servers/*fifo
#sleep 7
#echo "broadcast \"brainduck by ٭ıƞdex'<3 & Rapture (Brutal ★★✰✰✰)\"" > /home/teeworlds/servers/servers/*fifo
