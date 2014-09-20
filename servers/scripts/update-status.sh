#!/bin/sh
/home/teeworlds/servers/scripts/status.py > /var/www/status/index.tmp && mv /var/www/status/index.tmp /var/www/status/index.html

/home/teeworlds/servers/scripts/ddmax-status.py > /var/www/status/ddmax.tmp && mv /var/www/status/ddmax.tmp /var/www/status/ddmax.html

#/home/teeworlds/servers/scripts/konatbl4-status.py > /var/www/status/konatbl4.tmp
#mv /var/www/status/konatbl4.tmp /var/www/status/konatbl4.html

#/home/teeworlds/servers/scripts/wage-status.py > /var/www/status/wage.tmp
#mv /var/www/status/wage.tmp /var/www/status/wage.html
