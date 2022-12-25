#!/bin/sh
for loc in $(cat all-locations); do
  ssh $loc.ddnet.org servers/restart-ddnet-on-empty.sh
done
