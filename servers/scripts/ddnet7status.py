#!/usr/bin/env python3

import json
from collections import OrderedDict
from tw_api import *

doc = json.load(open("/home/teeworlds/servers/serverlist7.json"), object_pairs_hook=OrderedDict, object_hook=OrderedDict)
servers_info = []

def address(s):
    spl = s.split(':')
    return (spl[0], int(spl[1]))

for country in doc:
    for typ in country["servers"]:
        for server in country["servers"][typ]:
            s = Server_Info(address(server))
            servers_info.append((country["name"], s))
            s.start()

result = OrderedDict()
for country in doc:
    result[country["name"]] = []

while len(servers_info) != 0:
    servers_info[0][1].join()
    if servers_info[0][1].finished == True:
        if servers_info[0][1].info:
            result[servers_info[0][0]].append(servers_info[0][1].info)
        del servers_info[0]

for country in doc:
    result[country["name"]].sort(key=lambda x: x['address'])

print(json.dumps(result))
