#!/bin/sh

#echo "change_map Kobra 2" > servers/8303.fifo
#sleep 2
#echo 'sv_name "DDNet GER - Tournament #5 [DDraceNetwork]"
#exec motd/tournament.cfg
#sv_team 1
#sv_show_others_default 0
#sv_map_vote 0
#sv_reset_file reset.cfg
#clear_votes' > servers/8303.fifo

#echo "change_map Kobra" > servers/8304.fifo
#sleep 2
#echo 'sv_name "DDNet FRA - Tournament #2 [DDraceNetwork]"
#exec motd/tournament.cfg
#sv_team 1
#sv_show_others_default 0
#sv_map_vote 0
#sv_reset_file reset.cfg
#clear_votes' > servers/8304.fifo

#echo "change_map Kobra 2" > servers/8305.fifo
#sleep 2
#echo 'sv_name "DDNet FRA - Tournament #3 [DDraceNetwork]"
#exec motd/tournament.cfg
#sv_team 1
#sv_show_others_default 0
#sv_map_vote 0
#sv_reset_file reset.cfg
#clear_votes' > servers/8305.fifo

echo 'sv_name "DDNet GER - Tournament #6 [DDraceNetwork]"
exec motd/tournament.cfg
sv_team 1
sv_show_others_default 0
sv_map_vote 0
sv_reset_file reset.cfg
clear_votes' > servers/8304.fifo
