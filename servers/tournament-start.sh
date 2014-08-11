#!/bin/sh

echo 'change_map TEST4' > servers/8303.fifo
echo 'change_map TEST4' > servers/8304.fifo
echo 'change_map TEST4' > servers/8306.fifo
sleep 1
echo 'exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
echo 'exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
echo 'exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8306.fifo &
sleep 118
echo "change_map Neverwhere" > servers/8303.fifo
echo "change_map Neverwhere" > servers/8304.fifo
echo "change_map Neverwhere" > servers/8306.fifo
sleep 1
echo "change_map Neverwhere" > servers/8303.fifo
echo "change_map Neverwhere" > servers/8304.fifo
echo "change_map Neverwhere" > servers/8306.fifo
sleep 1
echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
echo 'pause_game; exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8306.fifo &
sleep 57
echo 'reload' > servers/8303.fifo
echo 'reload' > servers/8304.fifo
echo 'reload' > servers/8306.fifo
sleep 1
echo 'exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
echo 'exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
echo 'exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8306.fifo &
sleep 1
echo 'exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8303.fifo &
echo 'exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8304.fifo &
echo 'exec motd/tournament.cfg; sv_team 2; sv_show_others_default 0; clear_votes' > servers/8306.fifo &
