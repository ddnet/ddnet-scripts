#!/bin/sh
cd /home/teeworlds/servers && /home/teeworlds/servers/scripts/stats.py > /var/www/stats/index.$$.tmp && mv /var/www/stats/index.$$.tmp /var/www/stats/index.html
