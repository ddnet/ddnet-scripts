#!/bin/sh
DIR=/home/teeworlds/servers/test/maps
find $DIR -mtime +60 -type f -delete
rm -f $DIR/*\(1\).map $DIR/*\(2\).map $DIR/*\(3\).map $DIR/*\(4\).map $DIR/*\(5\).map
