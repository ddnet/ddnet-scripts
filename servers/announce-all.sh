#!/usr/bin/env zsh
set -e -x
rni 10 3

ssh ddnet.org "echo broadcast \\\"$@\\\" > servers/servers/*.fifo" &

for i in `cat ~/servers/all-locations`; do
  ssh $i.ddnet.org "echo broadcast \\\"$@\\\" > servers/servers/*.fifo" &
done
