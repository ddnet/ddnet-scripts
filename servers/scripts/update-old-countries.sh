#!/bin/bash

cd /home/teeworlds/servers || exit 1

countries=$(cat all-old-countries)
types=$(cat all-types)
for country in $countries; do
  scripts/ranks.py --country="$country" $types
done
