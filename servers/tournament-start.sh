#!/bin/sh

echo 'change_map TEST5' > servers/8303.fifo
#echo 'change_map TEST5' > servers/8304.fifo
#echo 'change_map TEST5' > servers/8305.fifo
#echo 'change_map TEST5' > servers/8308.fifo
sleep 1
echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8305.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8308.fifo &
sleep 58
echo "change_map Jvice" > servers/8303.fifo
#echo "change_map Jvice" > servers/8304.fifo
#echo "change_map Jvice" > servers/8305.fifo
#echo "change_map Jvice" > servers/8308.fifo
sleep 1
echo "change_map Jvice" > servers/8303.fifo
#echo "change_map Jvice" > servers/8304.fifo
#echo "change_map Jvice" > servers/8305.fifo
#echo "change_map Jvice" > servers/8308.fifo
sleep 1
echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
#echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
#echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8305.fifo &
#echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8308.fifo &
sleep 118
echo 'reload' > servers/8303.fifo
#echo 'reload' > servers/8304.fifo
#echo 'reload' > servers/8305.fifo
#echo 'reload' > servers/8308.fifo
sleep 1
echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8305.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8308.fifo &
sleep 1
echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8305.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 0; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8308.fifo &
