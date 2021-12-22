#!/bin/sh
cd /home/teeworlds/servers
echo '.dump --preserve-rowids' | sqlite3 /home/teeworlds/servers/ddnet-server-$1.sqlite | grep -E '^INSERT INTO record_(race|teamrace|saves)' | sed -e 's/INSERT INTO/INSERT IGNORE INTO/' | sed -e 's/rowid,//' -e 's/VALUES([0-9]*,/VALUES(/' > ddnet-server-$1.sql && mysql -u teeworlds -p'SECRETSQL' -h 168.119.96.247 teeworlds < ddnet-server-$1.sql && rm ddnet-server-$1.sql ddnet-server-$1.sqlite
