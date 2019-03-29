#!/bin/bash

if [ -z $1 ]; then
  printf "Err: Auth name not provided\n"
  exit
fi

for i in $(cat /home/teeworlds/servers/all-locations); do echo $i; ssh $i.ddnet.tw "echo auth_remove $1 >> servers/servers/*.fifo"; done
