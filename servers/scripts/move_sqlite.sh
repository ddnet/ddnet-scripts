#!/usr/bin/env zsh
cd /home/teeworlds/servers
scripts/move_sqlite.py
find . -maxdepth 1 -name 'ddnet-server-202*.sqlite' | while read i; do
  echo '.dump --preserve-rowids' | sqlite3 $i | grep -E '^INSERT INTO record_(race|teamrace|saves)' | sed -e 's/INSERT INTO/INSERT IGNORE INTO/' | sed -e 's/rowid,//' -e 's/VALUES([0-9]*,/VALUES(/' > ${i:r}.sql && mysql -u teeworlds -p'SECRETSQL' -h 157.90.254.235 teeworlds < ${i:r}.sql && rm $i ${i:r}.sql
done
