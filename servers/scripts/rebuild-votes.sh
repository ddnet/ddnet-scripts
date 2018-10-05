#!/bin/sh

for t in `cat all-types`; do
  tl=$(echo "$t" | tr A-Z a-z)
  /home/django/bin/print_mapfile $t > "/home/teeworlds/servers/types/$tl/maps"
done

