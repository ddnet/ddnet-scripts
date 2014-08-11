#!/bin/sh
while true; do
  nice -n -5 ./versionsrv >> /home/teeworlds/servers/versionsrv.log
  sleep 1
done
