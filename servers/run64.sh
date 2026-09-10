#!/bin/sh

LOG_DAYS=2 # Keep logs of the last 2 days

while true; do
  # Only update log.old file if the log file contains anything interesting,
  # being unable to start the server is uninteresting and can happen if we run
  # run64.sh again while servers are already up.
  if tail -n1 "servers/$1.log" | grep -aqv "E server: couldn't open socket"; then
    RE="^("
    for LOG_DAY in $(seq 0 "$LOG_DAYS"); do
      if [ "$LOG_DAY" -ne 0 ]; then
        RE="$RE|"
      fi
      RE="$RE$(date --date="$LOG_DAY day ago" '+%Y-%m-%d')"
    done
    RE="$RE) "
    mv "servers/$1.log" "servers/$1.log.tmp"
    cat "servers/$1.log.old" "servers/$1.log.tmp" | grep -aE "$RE" | tee "servers/$1.log.old"
    rm -f "servers/$1.log.tmp"
  fi
  rm -f "servers/$1.log"
  ps aux | grep -v grep | grep -q "./DDRace64-Server_sql -f servers/$1.cfg" && sleep 60 && continue
  ni -15 2 ./DDRace64-Server_sql -f "servers/$1.cfg" || true
  ps aux | grep -v grep | grep -q "./DDRace64-Server_sql -f servers/$1.cfg" || rm -f "servers/$1.fifo"
  sleep 1
done
