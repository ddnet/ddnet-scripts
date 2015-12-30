#!/bin/sh

echo 'change_map TEST8' > servers/8303.fifo
#echo 'change_map TEST8' > servers/8304.fifo
#echo 'change_map TEST8' > servers/8305.fifo
#echo 'change_map TEST8' > servers/8308.fifo
sleep 1
echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8305.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8308.fifo &
sleep 118
echo "sv_tournament_mode 1; change_map Squidgy" > servers/8303.fifo
#echo "sv_tournament_mode 1; change_map Squidgy" > servers/8304.fifo
#echo "sv_tournament_mode 1; change_map Squidgy" > servers/8305.fifo
#echo "sv_tournament_mode 1; change_map Squidgy" > servers/8308.fifo
sleep 1
echo "sv_tournament_mode 1; change_map Squidgy" > servers/8303.fifo
#echo "sv_tournament_mode 1; change_map Squidgy" > servers/8304.fifo
#echo "sv_tournament_mode 1; change_map Squidgy" > servers/8305.fifo
#echo "sv_tournament_mode 1; change_map Squidgy" > servers/8308.fifo
sleep 1
echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
#echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
#echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8305.fifo &
#echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes' > servers/8308.fifo &
sleep 118
echo 'sv_tournament_mode 0; reload' > servers/8303.fifo
#echo 'sv_tournament_mode 0; reload' > servers/8304.fifo
#echo 'sv_tournament_mode 0; reload' > servers/8305.fifo
#echo 'sv_tournament_mode 0; reload' > servers/8308.fifo
sleep 1
echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes; sv_reserved_slots 2; sv_reserved_slots_pass fürhallo' > servers/8303.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes; sv_reserved_slots 2; sv_reserved_slots_pass fürhallo' > servers/8304.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes; sv_reserved_slots 2; sv_reserved_slots_pass fürhallo' > servers/8305.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes; sv_reserved_slots 2; sv_reserved_slots_pass fürhallo' > servers/8308.fifo &
sleep 1
echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes; sv_reserved_slots 2; sv_reserved_slots_pass fürhallo' > servers/8303.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes; sv_reserved_slots 2; sv_reserved_slots_pass fürhallo' > servers/8304.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes; sv_reserved_slots 2; sv_reserved_slots_pass fürhallo' > servers/8305.fifo &
#echo 'exec motd/tournament.cfg; sv_team 2; sv_max_team_size 64; sv_show_others 1; sv_solo_server 0; sv_show_others_default 0; clear_votes; sv_reserved_slots 2; sv_reserved_slots_pass fürhallo' > servers/8308.fifo &
