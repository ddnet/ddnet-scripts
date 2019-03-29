#!/bin/sh
/home/teeworlds/servers/scripts/status.py > /var/www/status/index.$$.tmp && mv /var/www/status/index.$$.tmp /var/www/status/index.html
#curl -s -o /var/www/status/discord.$$.tmp "https://discordapp.com/api/guilds/252358080522747904/widget.png?style=banner2" && mv /var/www/status/discord.$$.tmp /var/www/status/discord.png
