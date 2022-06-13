#!/usr/bin/env python2
from mysql import *
import sys
import os
import json
from collections import defaultdict

con = mysqlConnect()
con.autocommit(True)
cur = con.cursor()
cur.execute("set names 'utf8mb4';")
cur.execute('create table if not exists record_playertimes(Name varchar(16) character set utf8mb4 collate utf8mb4_bin not null, Date date not null, SecondsPlayed int not null, primary key(Name, Date));')

dir = sys.argv[1]
players = defaultdict(int)
for file in os.listdir(dir):
    if not file.endswith('.json'):
        continue
    with open(os.path.join(dir, file), 'r') as f:
        print(file)
        try:
            j = json.load(f)
        except KeyboardInterrupt:
            raise
        except:
            continue
    playersNow = set()
    for server in j['servers']:
        for player in server['info']['clients']:
            # rstrip() because some servers allow trailing spaces, ddnet doesn't, and mysql considers strings the same if only trailing space differs
            name = player['name'].rstrip()
            if name not in playersNow:
                players[name] += 5
                playersNow.add(name)
for name, seconds in players.items():
    cur.execute('insert into record_playertimes values ("{}", "{}", {});'.format(con.escape_string(name.encode('utf-8')), con.escape_string(dir), seconds))
