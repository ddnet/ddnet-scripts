#!/bin/sh

cd ~/servers

#nohup ./run-versionsrv.sh &

#for i in `cat all-servers`; do
#  nohup ./run64.sh $i > /dev/null &
#done

#cd test

#for i in test test2; do
#  nohup ./run64.sh $i > /dev/null &
#done

#cd ~/testing/secret
#nohup ./run64.sh secret > /dev/null &

#cd ../secret2
#nohup ./run64.sh secret2 > /dev/null &
#
#cd ../secret3
#nohup ./run64.sh secret3 > /dev/null &

#cd ../secret4
#nohup ./run64.sh secret4 > /dev/null &
#
#cd ../secret5
#nohup ./run64.sh secret5 > /dev/null &

#cd ../secret6
#nohup ./run64.sh secret6 > /dev/null &
#
#cd ../secret7
#nohup ./run64.sh secret7 > /dev/null &

cd ~/servers
nohup ./serverstatus-client.py &

#sshfs -o reconnect testmaps@ddnet.tw:/home/teeworlds/servers/test/maps/ test/data/maps &
