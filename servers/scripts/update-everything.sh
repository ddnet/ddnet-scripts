#!/bin/bash

cd /home/teeworlds/servers

LOCK_FILE="scripts/ranks-lock"

# noclobber prevents the '>' from overwriting an existing lock file.
if ! (set -o noclobber; echo $$ > "$LOCK_FILE"); then
   echo -e "Already locked by the process with the PID $(cat "$LOCK_FILE"). Remove $LOCK_FILE to unlock manually."
   exit 1
fi

cleanup()
{
  rm -f "$LOCK_FILE"
}

trap cleanup EXIT HUP INT QUIT TERM # Always call, even on success.

types=`cat all-types`

scripts/update-local.sh

scripts/ranks.py $types
scripts/ranks.py --country=OLD $types
grep name serverlist.json | sed -e 's/.*"name": "\(.*\)".*/\1/' | while read country; do
  scripts/ranks.py --country=$country $types
done

scripts/releases-mappers.py $types > /var/www/mappers/index.$$.tmp && mv /var/www/mappers/index.$$.tmp /var/www/mappers/index.html

scripts/halloffame.py > /var/www/halloffame/index.html

#scripts/koule-tournament.py novice > /var/www/tournament/9/index.$$.tmp
#mv /var/www/tournament/9/index.$$.tmp /var/www/tournament/9/index.html
