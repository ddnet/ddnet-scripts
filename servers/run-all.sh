#!/bin/sh

cd /home/teeworlds/servers

nohup ./run-versionsrv.sh &

#for i in `cat all-servers`; do
#  nohup ./run64.sh $i > /dev/null &
#done

cd test

for i in test test2 test3; do
  nohup ./run64.sh $i > /dev/null &
done

cd ..

cd secret

for i in secret; do
  nohup ./run64.sh $i > /dev/null &
done

cd ..

nohup ./serverstatus-client.py &

#sshfs -o reconnect testmaps@ddnet.tw:/home/teeworlds/servers/test/maps/ test/data/maps &
