#!/bin/sh

set -ex
cd /home/teeworlds/servers/
cp "$1"/*.map maps/
./git-update-files-only.sh
