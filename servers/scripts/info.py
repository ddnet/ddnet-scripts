#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ddnet import *
from urllib.parse import parse_qs
import csv
import json
import os.path

serversDir = "/home/teeworlds/servers"

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
      query(("select Map from record_race where Name = '%s' group by Map;" % con.escape_string(result["name"]).decode('utf-8')).encode('utf-8'))
      result["maps"] = list(map(lambda row: row[0], cur.fetchall()))
    except Exception as e:
      print(e)

    try:
      query(("select Points from record_points where Name= '%s';" % con.escape_string(result["name"]).decode('utf-8')).encode('utf-8'))
      rows = cur.fetchall()
      result["points"] = rows[0][0] if len(rows) > 0 else 0
    except Exception as e:
      print(e)

  try:
    with open(os.path.join(serversDir, 'serverlist.json'), 'r', encoding='utf-8') as f:
      result["servers"] = json.load(f)

    with open(os.path.join(serversDir, 'serverlist-kog.json'), 'r', encoding='utf-8') as f:
      result["servers-kog"] = json.load(f)

    #if "name" in result:
    #  query("select Server from record_race where Name = '%s' and Server != '' and Server != 'UNK' group by Server order by count(*) desc;" % con.escape_string(result["name"]).decode('utf-8'))
    #  favorites = map(lambda row: row[0], cur.fetchall())

    #  def favKey(x):
    #    try:
    #      return favorites.index(x["name"])
    #    except:
    #      return len(list(favorites))

    #  result["servers"].sort(key=favKey)
  except Exception as e:
    print(e)

  try:
    with open(os.path.join(serversDir, 'news'), 'r', encoding='utf-8') as f:
      result["news"] = f.read()
  except Exception as e:
    print(e)

  try:
    country = env['HTTP_CF_IPCOUNTRY']
    result["map-download-url"] = 'https://ddnet-maps-1251829362.file.myqcloud.com' if country == 'CN' else 'https://maps.ddnet.org'
  except Exception as e:
    print(e)

  try:
    country = env['HTTP_CF_IPCOUNTRY'].lower()
    with open(os.path.join(serversDir, 'country_continent.csv'), newline='') as csvfile:
      country_continent = {row['country']: row['continent'] for row in csv.DictReader(csvfile)}
    result["location"] = country_continent[country]
  except Exception as e:
    print(e)


  try:
    with open('/var/www-update5/update.json', 'rb') as f:
      result["version"] = json.load(f)[0]["version"]
  except Exception as e:
    print(e)

  return [bytes(json.dumps(result, indent=4), 'utf-8')]
