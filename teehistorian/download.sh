#!/bin/sh
set -ue
#/usr/local/bin/rni 19 3
cd /media/teehistorian

rsync -a --no-o --no-g --append-verify --rsync-path='nice -n19 ionice -c3 rsync' -e 'ssh -o Compression=no' ddnet:/var/www/stats/master/\*.zstd /media/teehistorian/master &

mkdir -p data

#ssh ger1.ddnet.tw exit || true # Annoying DoS protection needs 2 connection attempts
for loc in $(cat all-locations); do
  # rsync's -z compression is better than ssh's -C
  rsync -z -a --bwlimit=256K --no-o --no-g -H --append-verify --rsync-path='nice -n19 ionice -c3 rsync' -e 'ssh -o Compression=no' -v "${loc}.ddnet.tw:servers/teehistorian/." "data/${loc}/" &
done

for dir in data/*; do
  if [ -d $dir -a ! -e $dir/index.txt ]; then
    echo "game_uuid,timestamp,map_name,map_crc,map_size" > $dir/index.txt
  fi
done

find data -name "*.teehistorian" -mtime +8 -exec ./archive.sh {} \;

wait # for rsyncs

for dir in data/*; do
  /media/teehistorian/teehistorian_index $dir | cut -d',' -f2- > $dir/index.new.txt
done

for i in data/*/index.txt data/*/index.new.txt; do
  echo $i
  (head -n 1 $i && tail -n +2 $i | sort --field-separator=',' --key=2,5 --key=1,1) > $i.$$.tmp && mv $i.$$.tmp $i
  gzip -9 < $i > $i.$$.gz && mv $i.$$.gz $i.gz
done
