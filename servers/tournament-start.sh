#!/bin/sh

cd /home/teeworlds/servers
echo 'change_map C_Loading' > servers/8303.fifo
#echo 'change_map C_Loading' > servers/8304.fifo
#echo 'change_map C_Loading' > servers/8305.fifo
#echo 'change_map C_Loading' > servers/8306.fifo
sleep 1
echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
#echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
#echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes' > servers/8305.fifo &
#echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes' > servers/8306.fifo &
sleep 118
echo "sv_tournament_mode 1; change_map Cerberus" > servers/8303.fifo
#echo "sv_tournament_mode 1; change_map Cerberus" > servers/8304.fifo
#echo "sv_tournament_mode 1; change_map Cerberus" > servers/8305.fifo
#echo "sv_tournament_mode 1; change_map Cerberus" > servers/8306.fifo
sleep 1
echo "sv_tournament_mode 1; change_map Cerberus" > servers/8303.fifo
#echo "sv_tournament_mode 1; change_map Cerberus" > servers/8304.fifo
#echo "sv_tournament_mode 1; change_map Cerberus" > servers/8305.fifo
#echo "sv_tournament_mode 1; change_map Cerberus" > servers/8306.fifo
sleep 1
echo 'pause_game; exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
#echo 'pause_game; exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
#echo 'pause_game; exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes' > servers/8305.fifo &
#echo 'pause_game; exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes' > servers/8306.fifo &
sleep 58
echo 'sv_tournament_mode 0; reload' > servers/8303.fifo
#echo 'sv_tournament_mode 0; reload' > servers/8304.fifo
#echo 'sv_tournament_mode 0; reload' > servers/8305.fifo
#echo 'sv_tournament_mode 0; reload' > servers/8306.fifo
sleep 1
echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes; sv_reserved_slots 3; sv_reserved_slots_pass cake' > servers/8303.fifo &
#echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes; sv_reserved_slots 3; sv_reserved_slots_pass cake' > servers/8304.fifo &
#echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes; sv_reserved_slots 3; sv_reserved_slots_pass cake' > servers/8305.fifo &
#echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes; sv_reserved_slots 3; sv_reserved_slots_pass cake' > servers/8306.fifo &
sleep 1
echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes; sv_reserved_slots 3; sv_reserved_slots_pass cake' > servers/8303.fifo &
#echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes; sv_reserved_slots 3; sv_reserved_slots_pass cake' > servers/8304.fifo &
#echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes; sv_reserved_slots 3; sv_reserved_slots_pass cake' > servers/8305.fifo &
#echo 'exec motd/tournament.cfg; sv_team 1; sv_min_team_size 4; sv_max_team_size 8; sv_show_others 1; sv_solo_server 0; sv_vote_kick 0; sv_map_vote 0; tune player_collision 1; tune player_hooking 1; sv_show_others_default 0; clear_votes; sv_reserved_slots 3; sv_reserved_slots_pass cake' > servers/8306.fifo &
