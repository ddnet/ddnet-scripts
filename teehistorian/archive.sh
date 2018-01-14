#!/bin/sh
echo "$1"
/media/teehistorian/teehistorian_index "$1" >> $(dirname "$1")/index.txt
xz -0 "$1"
