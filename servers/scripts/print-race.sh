#!/bin/sh

for f in /home/teeworlds/servers/servers/*.fifo
do
    echo 'broadcast "Hey DDNet! 2 more Race maps just released"' > "$f"
done
