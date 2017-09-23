#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
from urlparse import parse_qs
import sys
import json
import os.path

serversDir = "/home/teeworlds/servers"

reload(sys)
sys.setdefaultencoding('utf8')

def connect():
  global con, cur
  con = mysqlConnect()
  con.autocommit(True)
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

connect()
def query(sql):
  global con, cur
  try:
    cur.execute(sql)
  except:
    connect()
    cur.execute(sql)

def application(env, start_response):
  path = env['PATH_INFO']
  d = parse_qs(env['QUERY_STRING'])

  start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])

  result = {}

  if "name" in d:
    result["name"] = d["name"][0]

  if "name" in result:
    try:
      query("select Map from record_race where Name = '%s' group by Map;" % con.escape_string(result["name"]))
      result["maps"] = map(lambda row: row[0], cur.fetchall())
    except Exception as e:
      print(e)

  try:
    with open(os.path.join(serversDir, 'serverlist.json'), 'rb') as f:
      result["servers"] = json.load(f)

    if "name" in result:
      query("select Server from record_race where Name = '%s' and Server != '' and Server != 'UNK' group by Server order by count(*) desc;" % con.escape_string(result["name"]))
      favorites = map(lambda row: row[0], cur.fetchall())

      def favKey(x):
        try:
          return favorites.index(x["name"])
        except:
          return len(favorites)

      result["servers"].sort(key=favKey)
  except Exception as e:
    print(e)

  try:
    with open(os.path.join(serversDir, 'news'), 'rb') as f:
      result["news"] = f.read()
  except Exception as e:
    print(e)

  try:
    with open('/var/www-update4/update.json', 'rb') as f:
      result["version"] = json.load(f)[0]["version"]
  except Exception as e:
    print(e)

  return json.dumps(result)
