#!/usr/bin/env zsh
set -e -x
cd $HOME/servers
git pull
scripts/update-servers.sh
