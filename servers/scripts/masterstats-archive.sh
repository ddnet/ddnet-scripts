#!/bin/sh
cd /var/www/stats/master/
find * -type d -not -name $(date "+%Y-%m-%d") | while read date; do
  ~/servers/scripts/extract-master.py $date
  ZSTD_CLEVEL=19 tar --zstd -cf ~/$date.tar.zstd $date/* && mv ~/$date.tar.zstd $date.tar.zstd && mv $date ~ && rm -r ~/$date
done
