#!/bin/sh
FAILED_SQL=$HOME/servers/failed_sql.sql
test -e "$FAILED_SQL" && wc -l "$FAILED_SQL"
