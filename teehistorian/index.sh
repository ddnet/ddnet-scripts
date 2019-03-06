#!/bin/sh
xzcat "$1" | /media/teehistorian/teehistorian_index --ignore-ext - | tail -n-1 | cut -d',' -f2- >> $(dirname "$1")/index.new.txt
