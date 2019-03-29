#!/bin/bash

cd /home/teeworlds/servers

if [ $(cat /proc/loadavg|head -c1) -ge 2 ]; then
  #echo -e "Current load is > 2, not running."
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

scripts/update-local.sh

scripts/ranks.py $types
mv /var/www/players.msgpack.tmp /var/www/players.msgpack
#scp /var/www/players.msgpack can.ddnet.tw:/var/www/players.msgpack.tmp
#ssh can.ddnet.tw "mv /var/www/players.msgpack.tmp /var/www/players.msgpack"
scripts/ranks.py --country=OLD $types
grep name serverlist.json | sed -e 's/.*"name": "\(.*\)".*/\1/' | while read country; do
  scripts/ranks.py --country=$country $types
done

scripts/releases-mappers.py $types > /var/www/mappers/index.$$.tmp && mv /var/www/mappers/index.$$.tmp /var/www/mappers/index.html

scripts/halloffame.py > /var/www/halloffame/index.html
