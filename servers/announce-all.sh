#!/usr/bin/env zsh
set -e -x
rni 10 3

ssh ddnet.tw "echo broadcast \\\"$@\\\" > servers/servers/*.fifo" &

for i in `cat ~/servers/all-locations`; do
  ssh $i.ddnet.tw "echo broadcast \\\"$@\\\" > servers/servers/*.fifo" &
done
