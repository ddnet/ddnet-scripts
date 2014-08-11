#!/usr/bin/env zsh
rm -rf /home/teeworlds/maps
mkdir /home/teeworlds/maps
cd /home/teeworlds/maps

for i in `cat ../servers/all-types`; do
  mkdir $i
  grep "|" ../servers/types/$i/maps | cut -d"|" -f2 | while read j; do
    cp -- "../servers/maps/$j.map" $i
    cp -- "../servers/data/maps/$j.cfg" $i 2>/dev/null
    echo "add_vote \"$j\" change_map \"$j\"" >> $i/votes.cfg
  done
done

cd /home/teeworlds
zip -9r maps.zip maps
mv maps.zip /var/www/downloads
rm -rf maps
