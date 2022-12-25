#!/bin/sh
cd /home/teeworlds/servers
scripts/advent.py> /var/www/tournaments/advent2022/index.html.$$.tmp && mv /var/www/tournaments/advent2022/index.html.$$.tmp /var/www/tournaments/advent2022/index.html
