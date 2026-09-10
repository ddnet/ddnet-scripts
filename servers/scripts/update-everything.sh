#!/bin/bash

cd /home/teeworlds/servers

if [ $(cat /proc/loadavg|head -c1) -ge 15 ]; then
  #echo -e "Current load is > 15, not running."
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
scripts/players-cache.py
i=0
parallelism=10
# EUR is split into 5 regions in ranks:
(echo NLD; echo GER; echo POL; echo FRA; echo FIN; jq -r 'map(select(.id == "ddnet")).[0]["icon"]["servers"] | map(.name) .[]' ~httpmaster/communities-generated-backcompat.json) | while read country; do
  scripts/ranks.py --country=$country $types &
  if (( $i % $parallelism == 0 )); then
    wait
  fi
  let i=i+1
done

#scripts/halloffame.py > /var/www/halloffame/index.html
#scripts/update-stats.sh

(scripts/releases-mappers.py $types > /var/www/mappers/index.$$.tmp && mv /var/www/mappers/index.$$.tmp /var/www/mappers/index.html) &


wait
