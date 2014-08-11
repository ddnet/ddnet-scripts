#!/bin/sh

echo 'sv_team 1; sv_reset_file types/novice/flexreset.cfg; clear_votes; exec types/novice/flexvotes.cfg; exec types/novice/votes.cfg; exec data/maps/Kobra 2.map.cfg' > servers/8303.fifo
