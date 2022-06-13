#!/usr/bin/env zsh
set -e
mkdir -p ~/extract-master
cd ~/extract-master
for i in $*; do
  tar xvf $i
  ~/servers/scripts/extract-master.py ${i:t:r:r}
  rm -r ${i:t:r:r}
done
