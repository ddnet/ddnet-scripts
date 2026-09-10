#!/bin/sh
echo 'select * from record_race where Map not in (select Map from record_maps);' | mysql -u teeworlds -p'SECRETPASS' teeworlds
