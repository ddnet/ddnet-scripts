#!/usr/bin/env zsh
xzcat "$1" > /tmp/${1:t:r} && ./teehistorian_index /tmp/${1:t:r} | tail -n-1 | cut -d',' -f2- >> ${1:h}/index.txt && rm /tmp/${1:t:r}
