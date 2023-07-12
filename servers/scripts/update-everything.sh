#!/bin/bash

cd /home/teeworlds/servers

if [ $(cat /proc/loadavg|head -c1) -ge 8 ]; then
  #echo -e "Current load is > 8, not running."
  exit 1
fi

LOCK_FILE="scripts/ranks-lock"

# noclobber prevents the '>' from overwriting an existing lock file.
if ! (set -o noclobber; (echo $$ > "$LOCK_FILE") 2> /dev/null); then
  #echo -e "Already locked by the process with the PID $(cat "$LOCK_FILE"). Remove $LOCK_FILE to unlock manually."
  exit 1
fi

cleanup()
{
  rm -f "$LOCK_FILE"
}

trap cleanup EXIT HUP INT QUIT TERM # Always call, even on success.

types=`cat all-types`

scripts/update-local.sh &

scripts/ranks.py $types
i=0
# EUR is split into 4 regions in ranks:
(echo NLD; echo GER; echo POL; echo FRA; grep name serverlist.json | sed -e 's/.*"name": "\(.*\)".*/\1/') | while read country; do
  scripts/ranks.py --country=$country $types &
  if (( $i % 4 == 0 )); then
    wait
  fi
  let i=i+1
done

#scripts/halloffame.py > /var/www/halloffame/index.html
#scripts/update-stats.sh

(scripts/releases-mappers.py $types > /var/www/mappers/index.$$.tmp && mv /var/www/mappers/index.$$.tmp /var/www/mappers/index.html) &

(zip -q9r /var/www/players-cache.$$.tmp players-cache && mv /var/www/players-cache.$$.tmp /var/www/players-cache.zip) &

(curl -s -o serverlist-kog.json.$$.tmp http://51.91.78.232/servers.php && jq . serverlist-kog.json.$$.tmp > /dev/null  && mv serverlist-kog.json.$$.tmp serverlist-kog.json && ./git-update-serverlist-only.sh) &

wait
