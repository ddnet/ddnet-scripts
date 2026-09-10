#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ddnet import *
import datetime
import sys
import random
import re
import os
from contextlib import nullcontext

sys.stdout.reconfigure(encoding='utf-8')

countryCodeMapping = {
        'NLD': '🇳🇱',
        'GER': '🇩🇪',
        'POL': '🇵🇱',
        'FIN': '🇫🇮',
        'FRA': '🇫🇷',
        'RUS': '🇷🇺',
        'UKR': '🇺🇦',
        'TUR': '🇹🇷',
        'IRN': '🇮🇷',
        'CHL': '🇨🇱',
        'BRA': '🇧🇷',
        'ARG': '🇦🇷',
        'COL': '🇨🇴',
        'CRI': '🇨🇷',
        'MEX': '🇲🇽',
        'PER': '🇵🇪',
        'USA': '🇺🇸',
        'CAN': '🇨🇦',
        'CHN': '🇨🇳',
        'KOR': '🇰🇷',
        'JAP': '🇯🇵',
        'TWN': '🇹🇼',
        'SGP': '🇸🇬',
        'ZAF': '🇿🇦',
        'AUS': '🇦🇺',
        'IND': '🇮🇳',
        'BHR': '🇧🇭',
}

htmlRanksPathTmp = "%s.%d.tmp" % (htmlRanksPath, os.getpid())
feedPath = '/var/www/status/records/feed/index.atom'
feedPathTmp = "%s.%d.tmp" % (feedPath, os.getpid())

def escapeMarkdown(name):
    return re.sub(r'([`~_\*|])', r'\\\1', name)

def postRecord(row, namesDiscord, namesHtml, namesTitle):
  if row[4].startswith("5"):
    oldTimeString = "next worst time: %s" % formatTimeExact(row[6])
  if row[4].startswith("3") or row[4].startswith("4"):
    oldTimeString = "%d points" % row[7]
  elif not row[6]:
    oldTimeString = "only finish!"
  elif row[6] == row[2]:
    oldTimeString = "tie!"
    return # too spammy
  else:
    oldTimeString = "next best time: %s" % formatTimeExact(row[6])

  if row[4].startswith("5"):
    improvementString = ' - %.1f%% deterioration!' % (-(1 - row[2] / row[6]) * 100) if row[6] else ''
  else:
    improvementString = ' - %.1f%% improvement!' % ((1 - row[2] / row[6]) * 100) if row[6] else ''

  msg = r"%s %s on \[[%s](<https://ddnet.org/ranks/%s/>)\] [%s](<https://ddnet.org%s>): %s %s (%s%s)" % (countryCodeMapping.get(row[8][:3], ''), row[4][2:], row[5], row[5].lower(), row[1], mapWebsite(row[1]), formatTimeExact(row[2]), namesDiscord, oldTimeString, improvementString)
  postDiscordRecords(msg)

  content = '<img src="/countryflags/%s.png" alt="%s" height="20" /> %s on [<a href="https://ddnet.org/ranks/%s/">%s</a>] <a href="https://ddnet.org%s">%s</a>: %s %s (%s%s)' % (row[8], row[8], row[4][2:], row[5].lower(), row[5], mapWebsite(row[1]), row[1], formatTimeExact(row[2]), namesHtml, oldTimeString, improvementString)
  title = '[%s] %s on [%s] %s: %s %s (%s%s)' % (row[8], row[4][2:], row[5], row[1], formatTimeExact(row[2]), namesTitle, oldTimeString, improvementString)

  with open(htmlRanksPath, 'a+', encoding='utf-8') as f:
    print('%s\x1e%s\x1e%s' % (formatDateExact(row[3]), content, title), file=f)

os.chdir("/home/teeworlds/servers/")

con = mysqlConnect()

# mysqlclient 2.x (py3) dropped the Connection context-manager protocol that
# py2 MySQLdb had. The block below is read-only, so keep the implicit single
# transaction open for a consistent snapshot (matching the old `with con:`).
with nullcontext():
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  with open("scripts/discord-ranks-last", 'r+') as f:
    startTime = parseDatetime(f.read().rstrip())
    endTime = datetime.datetime.now()
    f.seek(0)
    f.write(formatDateExact(endTime))
    f.truncate()

  rows = getRecords(cur, startTime, endTime)
  countFinishes = len(rows)
  currentRank = 0
  currentPosition = 0
  lastTime = 0
  skips = 1

  namesDiscord = []
  namesHtml = []
  namesTitle = []

  for i, row in enumerate(rows):
    if row[4].startswith("3") or row[4].startswith("1"):
      namesDiscord.append("[%s](<https://ddnet.org%s>)" % (escapeMarkdown(row[0]), playerWebsite(row[0])))
      namesHtml.append('<a href="https://ddnet.org%s">%s</a>' % (playerWebsite(row[0]), escape(row[0])))
      namesTitle.append(row[0])
      if i+1 >= len(rows) or rows[i+1][1] != row[1] or rows[i+1][2] != row[2]:
        postRecord(row,
            makeAndString(namesDiscord),
            makeAndString(namesHtml, ampersand = "&amp;"),
            makeAndString(namesTitle))
        namesDiscord = []
        namesHtml = []
        namesTitle = []
    else:
      postRecord(row,
        "[%s](<https://ddnet.org%s>)" % (escapeMarkdown(row[0]), playerWebsite(row[0])),
        '<a href="https://ddnet.org%s">%s</a>' % (playerWebsite(row[0]), escape(row[0])),
        row[0])

try:
  with open(htmlRanksPath, 'r+', encoding='utf-8') as f:
    lines = []
    endTime = datetime.datetime.now() - datetime.timedelta(weeks=1)
    for line in f:
      [timeStr, content] = line.strip().split('\x1e', 1)
      if parseDatetime(timeStr) > endTime:
        lines.append(line)
  with open(htmlRanksPathTmp, 'w', encoding='utf-8') as f:
      f.writelines(lines)
  os.rename(htmlRanksPathTmp, htmlRanksPath)
except IOError:
  pass

try:
  with open(htmlRanksPath, 'r+', encoding='utf-8') as f, open(feedPathTmp, 'w+', encoding='utf-8') as fatom:
    print("""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>DDraceNetwork Top Records</title>
  <link href="http://ddnet.org/status/records/feed/" rel="self" />
  <link href="http://ddnet.org/status/" />
  <id>http://ddnet.org/status/</id>
  <updated>%s</updated>
""" % formatDateExact(datetime.datetime.now()), file=fatom)

    p = re.compile('href="https://ddnet.org/maps/[^/]*/"')
    for line in reversed(f.readlines()):
      [timeStr, content, title] = line.strip().split('\x1e', 2)
      dt = parseDatetime(timeStr)
      m = p.search(content)
      link = m.group()

      #title = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*/>', '[\g<1>]', content)
      #title = re.sub(r'<a [^>]*>', '', title)
      #title = re.sub(r'</a>', '', title)
      #title = re.sub(r'&amp;', '&', title)

      print("""  <entry>
    <updated>%s</updated>
    <title>
      %s
    </title>
    <link %s />
    <content type="html">
      %s
    </content>
  </entry>
""" % (formatDateFeedStr(formatDate(dt)), escape(title), link, escape(content)), file=fatom)

    print("</feed>", file=fatom)
  os.rename(feedPathTmp, feedPath)
except IOError:
  pass
