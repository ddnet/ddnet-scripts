#!/bin/sh
set -u
set -e
cd /media/teehistorian
mkdir -p data
for loc in $(cat locations); do
  rsync -a --bwlimit=100K --no-o --no-g -H --append-verify -v "${loc}.ddnet.tw:servers/teehistorian/." "data/${loc}/" &
done
find data -name "*.teehistorian" -mtime +8 -exec ./archive.sh {} \;
