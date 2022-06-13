#!/usr/bin/env python3


import io
import sys
import re

from collections import namedtuple

class Player:

    def __init__(self, cid, ip, name=None, authlevel=None):
        self.ip = ip
        self.cid = cid
        self.name = name
        self.authlevel = authlevel

    def __str__(self):
        return '{} {} {}'.format(self.name, self.ip, self.authlevel)

PLAYERS = {}
LAST_ADDED = None


def ready(match):
    global LAST_ADDED
    LAST_ADDED = Player(match.group(1), match.group(2))
    PLAYERS[match.group(1)] = LAST_ADDED

def join(match):
    global LAST_ADDED
    LAST_ADDED.name = match.group(1)

def authed(match):
    PLAYERS[match.group(1)].authlevel = match.group(2)
    print(PLAYERS[match.group(1)])


# this one filters messages like:
# [16-09-09 09:42:51][server]: player is ready. ClientID=1 addr=79.50.24.16:49462 secure=yes
# it will create matchinggroups for ClientID and IP
re_ready = re.compile((
    r'\[.+\]\[server\]: player is ready\. ClientID=(\d+) '
    r'addr=(\d+\.\d+\.\d+.\d+):'
))

re_join = re.compile((
    r'\[.+\]\[chat\]: \*\*\* \'(.+)\' entered and joined the \w+$'
))

# [16-09-09 14:04:35][server]: ClientID=23 authed (moderator)
re_authed = re.compile((
    r'\[.+\]\[server\]: ClientID=(\d+) authed \((\w+)\)'
))


RE_LIST = [
    (re_ready, ready),
    (re_join, join),
    (re_authed, authed)
]

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

for line in input_stream:
    for regex, func in RE_LIST:
        match = regex.match(line)
        if match:
            func(match)
            break
