#!/bin/sh

set -ex
cd /home/teeworlds/servers/

cp "$1"/*.map maps/
git add maps/
cp "$1"/*.msgpack maps/
cp "$1"/*.png /var/www/ranks/maps/

cd "$1/types"
for t in *;
  do cp "$t" "/home/teeworlds/servers/types/$t/maps";
done

cd /home/teeworlds/servers/
./git-update.sh
