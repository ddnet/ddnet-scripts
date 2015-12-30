#!/usr/bin/env zsh
mkdir -p /home/teeworlds/maps
cd /home/teeworlds/maps
rm -rf *

for i in `cat ../servers/all-types`; do
  mkdir -p ${i:l}
  grep "|" ../servers/types/${i:l}/maps | cut -d"|" -f2 | while read j; do
    cp -- "../servers/maps/$j.map" ${i:l}
    #cp -- "../servers/data/maps/$j.cfg" ${i:l} 2>/dev/null
    echo "add_vote \"$j\" change_map \"$j\"" >> ${i:l}/votes.cfg
    sleep 0.2
  done
done

git add * &>/dev/null
git commit -a -m "upd" &>/dev/null
git push &>/dev/null
