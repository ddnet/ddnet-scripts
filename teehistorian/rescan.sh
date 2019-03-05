#!/bin/sh
# To be used when index.txt file has been lost
find data -name '*.teehistorian.xz' -print0 | xargs -L 1 -n 1 -0 -P 4 ./index.sh
