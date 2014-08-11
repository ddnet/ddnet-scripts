#!/bin/sh

#echo "change_map For Idiots 2" > servers/8303.fifo
#sleep 2
#echo 'sv_name "DDNet GER - Tournament #1 [DDraceNetwork]"
#exec motd/tournament.cfg
#sv_team 1
#sv_show_others_default 0
#sv_map_vote 0
#sv_reset_file reset.cfg
#clear_votes' > servers/8303.fifo
#
#echo "change_map Sunday" > servers/8304.fifo
#sleep 2
#echo 'sv_name "DDNet GER - Tournament #2 [DDraceNetwork]"
#exec motd/tournament.cfg
#sv_team 1
#sv_show_others_default 0
#sv_map_vote 0
#sv_reset_file reset.cfg
#clear_votes' > servers/8304.fifo

echo "change_map Rapture" > servers/8306.fifo
sleep 2
echo 'sv_name "DDNet GER - Tournament #3 [DDraceNetwork]"
exec motd/tournament.cfg
sv_team 1
sv_show_others_default 0
sv_map_vote 0
sv_reset_file reset.cfg
clear_votes' > servers/8306.fifo
