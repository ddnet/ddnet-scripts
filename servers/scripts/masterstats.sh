#!/bin/sh
TIMESTAMP=`sleepenh 0`
while true; do
  DIR=/var/www/stats/master/$(date "+%Y-%m-%d")
  (mkdir -p $DIR && cp /var/www-master1/ddnet/15/servers.json $DIR/$(date "+%H_%M_%S").json) &
  TIMESTAMP=$(sleepenh $TIMESTAMP 5.0)
done
