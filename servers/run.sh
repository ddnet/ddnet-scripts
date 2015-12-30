#!/bin/sh
while true; do
  mv servers/$1.log servers/$1.log.old
  ni -15 2 ./DDRace-Server_sql -f servers/$1.cfg
  sleep 1
done
