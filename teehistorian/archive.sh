#!/bin/sh
echo "$1"
/media/teehistorian/teehistorian_index "$1" | tail -n-1 | cut -d',' -f2- >> $(dirname "$1")/index.txt
xz -0f "$1"
