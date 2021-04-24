#!/usr/bin/env python2
from ddnet import *

with open("out.txt") as f:
    #list = ', '.join(["'" + x.strip() + "'" for x in f.readlines()])
    list2 = ' or '.join(["Savegame like '%" + x.strip() + "%'" for x in f.readlines()])

con = mysqlConnect()
con.autocommit(True)
cur = con.cursor()
cur.execute("set names 'utf8mb4';")
#cur.execute("select record_teamrace.Map, GameID, record_teamrace.Name, record_teamrace.Time, record_teamrace.Timestamp, record_maps.Server from record_teamrace inner join record_maps on record_teamrace.Map = record_maps.Map where GameID in ({}) order by Timestamp asc".format(list))
#rows = cur.fetchall()
#for row in rows:
#    map = row[0]
#    gameid = row[1]
#    name = row[2]
#    time = row[3]
#    timestamp = row[4]
#    server = row[5]
#    cur.execute("select Rank from (select rank() over w as Rank, Name, min(Time) as Time, GameID from record_teamrace where Map = '{}' group by Name window w as (order by Time)) as a where Name = '{}' and GameID = '{}';".format(con.escape_string(map), con.escape_string(name), con.escape_string(gameid)))
#    rows = cur.fetchall()
#    if rows and rows[0][0] <= 50:
#        print "{},{},{},{},{},{}".format(map, gameid, name, time, timestamp, rows[0][0])
#    elif server == 'Insane':
#        print "{},{},{},{},{}".format(map, gameid, name, time, timestamp)
#print "select * from record_saves where {};".format(list2)
cur.execute("select * from record_saves where {};".format(list2))
rows = cur.fetchall()
for row in rows:
    print row
