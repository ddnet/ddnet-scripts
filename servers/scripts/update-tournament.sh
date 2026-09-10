#!/bin/bash

cd /home/teeworlds/servers
scripts/tournament.py Brutal > /var/www/tournaments/65/index.$$.tmp && mv /var/www/tournaments/65/index.$$.tmp /var/www/tournaments/65/index.html
