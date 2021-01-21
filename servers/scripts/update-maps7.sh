#!/usr/bin/env zsh
set -x
rni 10 3

echo "Not used anymore, see git-update-files-only.sh"
exit 1

cd ~/servers
rm -f maps7.log
for i in maps/*.map; do
  j=~/servers7/maps/${i:t}
  ./map_convert_07 $i $j.tmp >> maps7.log && mv $j.tmp $j
done

cd ~/servers7
git add maps/*.map
git commit -a -m "upd"
git push

servers=0
for i in `cat ~/servers/all-locations`; do
  ssh $i.ddnet.tw "cd servers7; ni 10 3 git pull"
  if [ $? -eq 0 ]; then
    echo -e "\e[1;32m$i updated successfully\e[0m"
    servers=$((servers+1))
  else
    echo -e "\e[1;33mUpdating $i failed\e[0m"
  fi
done

wait
echo -e "\e[1;31m$servers/$(wc -w < all-locations) servers updated successfully\e[0m"

cd
rm -rf maps7
mkdir maps7
cp -- servers7/maps/*.map maps7
zip -9rq maps7.zip maps7
rm -rf maps7
mv maps7.zip /var/www-maps/compilations/
