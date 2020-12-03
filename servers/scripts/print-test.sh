#!/bin/sh

for f in /home/teeworlds/servers/servers/test*fifo
do
    echo 'broadcast "If you test tell the mapper or on trac about bugs and improvements""' > "$f"
done

