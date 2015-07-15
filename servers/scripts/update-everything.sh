#!/bin/bash

cd /home/teeworlds/servers

types=`cat all-types`

scripts/update-local.sh

scripts/ranks.py $types > /var/www/ranks/index.$$.tmp && mv /var/www/ranks/index.$$.tmp /var/www/ranks/index.html

scripts/releases-mappers.py $types > /var/www/mappers/index.$$.tmp && mv /var/www/mappers/index.$$.tmp /var/www/mappers/index.html

scripts/halloffame.py > /var/www/halloffame/index.html

#scripts/koule-tournament.py novice > /var/www/tournament/9/index.$$.tmp
#mv /var/www/tournament/9/index.$$.tmp /var/www/tournament/9/index.html
