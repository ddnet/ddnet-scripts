#!/bin/sh
cd /home/teeworlds/servers || exit 1

serial=$(head -n1 bans-global.cfg | cut -c2-)

case $serial in
  ''|*[!0-9]*) exit 1 ;;
esac

[ -f ".last-update" ] || exit 1

last=$(cat .last-update)
case $last in
  ''|*[!0-9]*) exit 1 ;;
esac

if [ "$serial" -lt "$last" ]; then
  exit 0
fi

./git-update-files-only.sh
rc=$?
if [ "$rc" -eq "0" ]; then
  date +'%s' > .last-update
  exit $rc
else
  exit 1
fi
