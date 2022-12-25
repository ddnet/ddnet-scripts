#!/usr/bin/env python3

import json
import subprocess

with open('/var/www-master1/ddnet/15/servers.json') as f:
    servers = json.load(f)
with open('/home/teeworlds/servers/serverlist.json') as f:
    ddnet = json.load(f)
with open('/home/teeworlds/servers/serverlist-kog.json') as f:
    kog = json.load(f)

good_names = set()
good_ips = set()
good_names.add('DDNET GER10 - Novice')
good_names.add('DDNET GER10 - Brutal')
good_names.add('DDNET GER10 - Solo')

for country in ddnet + kog:
    for typ in country['servers']:
        for good_addr in country['servers'][typ]:
            good_ips.add(good_addr.split(':')[0])
            for server in servers['servers']:
                for addr in server['addresses']:
                    if addr.split('/')[2] == good_addr:
                        good_names.add(server['info']['name'])
                        break

bad_ips = {}
for server in servers['servers']:
    if server['info']['name'] in good_names:
        found_good = False
        for addr in server['addresses']:
            if addr.split('/')[2].split(':')[0] in good_ips:
                found_good = True
                break
        if not found_good:
            for addr in server['addresses']:
                bad_ips[addr.split('/')[2].split(':')[0]] = server['info']['name']

for ip, name in bad_ips.items():
    cmd = ['/usr/sbin/ip', 'netns', 'exec', 'vpn', '/usr/sbin/ipset', 'add', 'fake', ip]
    # ipset v7.10: Comment cannot be used: set was created without comment support
    #cmd = ['/usr/sbin/ip', 'netns', 'exec', 'vpn', '/usr/sbin/ipset', 'add', 'fake', ip, 'comment', name]
    result = subprocess.run(cmd, capture_output=True)
    print(result)
    print("  Faking " + name)
