#!/bin/sh

cd /home/teeworlds/servers

nohup ./run-versionsrv.sh &

for i in `cat all-servers`; do
  nohup ./run64.sh $i > /dev/null &
done

cd test

for i in test test2 test3; do
  nohup ./run64.sh $i > /dev/null &
done

cd ../secret

for i in secret; do
  nohup ./run64.sh $i > /dev/null &
done

#cd ../secret2
#
#for i in secret2; do
#  nohup ./run64.sh $i > /dev/null &
#done

#cd ../secret3
#
#for i in secret3; do
#  nohup ./run64.sh $i > /dev/null &
#done

cd ..

for i in block; do
  nohup ./run64.sh $i > /dev/null &
done

nohup ./serverstatus-client.py &
