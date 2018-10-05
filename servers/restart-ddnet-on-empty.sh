#!/bin/sh
for fifo in ~/servers/servers/*.fifo; do
  echo "sv_shutdown_when_empty 1" > "$fifo"
done
