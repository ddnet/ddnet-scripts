#!/bin/sh
/home/teeworlds/servers/scripts/status.py > /var/www/status/index.$$.tmp && mv /var/www/status/index.$$.tmp /var/www/status/index.html
