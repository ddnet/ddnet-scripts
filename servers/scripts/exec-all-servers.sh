#!/bin/bash

if [ -z "$1" ]; then
  printf "Err: command not provided\n"
  exit
fi

for i in $(cat /home/teeworlds/servers/all-locations); do echo $i; ssh $i.ddnet.org "echo $1 >> servers/servers/*.fifo"; done
