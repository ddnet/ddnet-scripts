#!/bin/sh

while IFS= read -r t
do
  tl=$(echo "$t" | tr '[:upper:]' '[:lower:]')
  /home/django/bin/print_mapfile "$t" > "/home/teeworlds/servers/types/$tl/maps"
done < all-types

