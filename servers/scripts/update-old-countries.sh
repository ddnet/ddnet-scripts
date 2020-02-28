#!/bin/bash

cd /home/teeworlds/servers

countries=`cat all-old-countries`
types=`cat all-types`
for country in $countries; do
  scripts/ranks.py --country=$country $types
done
