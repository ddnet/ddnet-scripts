#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ddnet import *
from urllib.parse import parse_qs
import csv
import json
import os.path
import re

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

DDNET_VERSION_RE = re.compile(r"DDNet ([0-9]+)(?:\.([0-9]+))?")

def application(env, start_response):
  path = env['PATH_INFO']
  d = parse_qs(env['QUERY_STRING'])

  start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])

  ddnet_version = DDNET_VERSION_RE.match(env.get('HTTP_USER_AGENT', ''))
  if ddnet_version is not None:
    ddnet_major = int(ddnet_version.group(1))
    ddnet_minor = ddnet_version.group(2)
    if ddnet_minor is not None:
      ddnet_minor = int(ddnet_minor)
    else:
      ddnet_minor = 0
    ddnet_version = (ddnet_major, ddnet_minor)

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
    with open('/home/httpmaster/communities-generated-backcompat.json', 'r', encoding='utf-8') as f:
      communities = f.read()
    communities = json.loads(communities)
    ddnet_community = None
    kog_community = None
    for community in communities:
      if community["id"] == "ddnet":
        if ddnet_community is None:
          ddnet_community = community
        else:
          raise ValueError("duplicate ddnet community")
      elif community["id"] == "kog":
        if kog_community is None:
          kog_community = community
        else:
          raise ValueError("duplicate kog community")
    result["communities"] = communities
    if ddnet_community is not None:
      result["servers"] = ddnet_community["icon"]["servers"]
      del ddnet_community["icon"]["servers"]
    if kog_community is not None:
      result["servers-kog"] = kog_community["icon"]["servers"]
      del kog_community["icon"]["servers"]
  except Exception as e:
    print(e)

  result["community-icons-download-url"] = "https://info.ddnet.org/icons"

  try:
    with open(os.path.join(serversDir, 'generated/news'), 'r', encoding='utf-8') as f:
      result["news"] = f.read()
  except Exception as e:
    print(e)

  try:
    country = env['HTTP_CF_IPCOUNTRY']
    result["map-download-url"] = 'https://ddracenetwork.cdn.dfyun.com.cn' if country == 'CN' else 'https://maps.ddnet.org'
  except Exception as e:
    print(e)

  #try:
  #  result["connecting-ip"] = env['HTTP_CF_CONNECTING_IP']
  #except Exception as e:
  #  print(e)

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

  try:
    with open(os.path.join(serversDir, 'info-extra.json'), 'rb') as f:
      for k, v in json.load(f).items():
        result[k] = v
  except Exception as e:
    print(e)

  return [bytes(json.dumps(result, indent=4), 'utf-8')]
