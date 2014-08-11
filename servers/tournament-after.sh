#!/bin/sh

echo 'exec motd/tournament.cfg
clear_votes' > servers/8303.fifo

#echo 'change_map DreamWorld
#sv_name "DDraceNetwork GER - Tournament Brutal"
#exec motd/tournament-brutal.cfg
#sv_show_others_default 0
#sv_team 1
#sv_reset_file reset.cfg
#clear_votes' > servers/8304.fifo
