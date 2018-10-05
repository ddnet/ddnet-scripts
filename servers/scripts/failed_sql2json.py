#!/usr/bin/env python3

import sys
import json

racestr = 'INSERT IGNORE INTO %s_race(Map, Name, Timestamp, Time, Server, cp1, cp2, cp3, cp4, cp5, cp6, cp7, cp8, cp9, cp10, cp11, cp12, cp13, cp14, cp15, cp16, cp17, cp18, cp19, cp20, cp21, cp22, cp23, cp24, cp25) VALUES ('
uuidstr = 'SET @id = UUID();\n'
teamracestr = 'INSERT IGNORE INTO %s_teamrace(Map, Name, Timestamp, Time, ID) VALUES ('

def de_escape(s):
    return s.replace("\\\\", "\\").replace("\\'", "'").replace("\\\"", "\"")

for line in sys.stdin:
    if line.startswith(racestr):
        line = line[len(racestr)+1:-4]
        args = [de_escape(i) for i in line.split("', '")]
        data = {}
        data['type'] = 'rank'
        data['Map'] = args[0]
        data['Name'] = args[1]
        data['Timestamp'] = args[2]
        data['Time'] = float(args[3])
        data['Server'] = args[4]
        for i in range(0, 25):
            data['cp%d' % i] = float(args[4 + i +1])
    elif line == uuidstr:
        data = {}
        data['Names'] = []
        for l in sys.stdin:
            if l.startswith(teamracestr):
                l = l[len(teamracestr)+1:-9]
                args = [de_escape(i) for i in l.split("', '")]
                data['Names'].append(args[1])
            else:
                break
        data['type'] = 'teamrank' 
        data['Map'] = args[0]
        data['Timestamp'] = args[2]
        data['Time'] = float(args[3])

    print(json.dumps(data, ensure_ascii=False))

           

