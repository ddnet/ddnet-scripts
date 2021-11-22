#!/usr/bin/env python3
import json
import os
import os.path
import collections

path = "json"
comments = collections.Counter()
ready = collections.Counter()
for filename in os.listdir(path):
    r = None
    mapname = os.path.splitext(filename)[0]
    with open(os.path.join(path, filename), 'r') as json_file:
        j = json.load(json_file)
    for message in j["messages"]:
        #if "Tester" not in message["author"]["roles"]:
        #    continue
        testername = message["author"]["name"]
        if testername == "DDNet":
            continue
        comments[testername] += 1
        for x in message["content"]:
            for y in x.get("text", []):
                for z in y:
                    if type(y[z]) == str and y[z].startswith("$ready"):
                        r = testername
                    if type(y[z]) == dict and y[z].get("text", "").startswith("$ready"):
                        r = testername
    if r:
        ready[r] += 1
print(comments.most_common(20))
print(ready.most_common(20))
