#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import datetime
import sys
import random
import re
import os

reload(sys)
sys.setdefaultencoding('utf8')

countryCodeMapping = {
    'GER': '🇩🇪',
    'RUS': '🇷🇺',
    'CHL': '🇨🇱',
    'BRA': '🇧🇷',
    'USA': '🇺🇸',
    'CAN': '🇨🇦',
    'ZAF': '🇿🇦',
    'CHN': '🇨🇳',
    'GER2': '🇩🇪',
}

htmlRanksPathTmp = "%s.%d.tmp" % (htmlRanksPath, os.getpid())
feedPath = '/var/www/status/records/feed/index.atom'
feedPathTmp = "%s.%d.tmp" % (feedPath, os.getpid())

def escapeMarkdown(name):
    return re.sub(r'([`~_\*|])', r'\\\1', name)

def postRecord(row, namesDiscord, namesHtml, namesTitle):
  if row[4].startswith("3") or row[4].startswith("4"):
    oldTimeString = "%d points" % row[7]
  elif not row[6]:
    oldTimeString = "only finish!"
  elif row[6] == row[2]:
    oldTimeString = "tie!"
  else:
    oldTimeString = "next best time: %s" % formatTimeExact(row[6])

  msg = "%s %s on \[[%s](<https://ddnet.tw/ranks/%s/>)\] [%s](<https://ddnet.tw/ranks/%s/#map-%s>): %s %s (%s)" % (countryCodeMapping.get(row[8], ''), row[4][2:], row[5], row[5].lower(), row[1], row[5].lower(), normalizeMapname(row[1]), formatTimeExact(row[2]), namesDiscord, oldTimeString)
  postDiscordRecords(msg)

  if row[6]:
    improvement = (1 - row[2] / row[6]) * 100
    if improvement >= 15:
      msg += ' // %d%% improvement' % improvement
      if improvement >= 30:
        msg = '**%s**' % msg
      postDiscordSuspicious(msg)

  content = '<img src="/countryflags/%s.png" alt="%s" height="20" /> %s on [<a href="https://ddnet.tw/ranks/%s/">%s</a>] <a href="https://ddnet.tw/ranks/%s/#map-%s">%s</a>: %s %s (%s)' % (row[8], row[8], row[4][2:], row[5].lower(), row[5], row[5].lower(), normalizeMapname(row[1]), row[1], formatTimeExact(row[2]), namesHtml, oldTimeString)
  title = '[%s] %s on [%s] %s: %s %s (%s)' % (row[8], row[4][2:], row[5], row[1], formatTimeExact(row[2]), namesTitle, oldTimeString)

  with open(htmlRanksPath, 'a+') as f:
    print >>f, '%s\x1e%s\x1e%s' % (formatDateExact(row[3]), content, title)

os.chdir("/home/teeworlds/servers/")

con = mysqlConnect()

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  with open("scripts/discord-ranks-last", 'r+') as f:
    startTime = parseDatetime(f.read().rstrip())
    # give mysql replication 1 minute to get the rank over to us, otherwise we
    # won't see it here
    endTime = datetime.datetime.now() - datetime.timedelta(minutes=1)
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
      namesDiscord.append("[%s](<https://ddnet.tw%s>)" % (escapeMarkdown(row[0]), playerWebsite(row[0])))
      namesHtml.append('<a href="https://ddnet.tw%s">%s</a>' % (playerWebsite(row[0]), escape(row[0])))
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
        "[%s](<https://ddnet.tw%s>)" % (escapeMarkdown(row[0]), playerWebsite(row[0])),
        '<a href="https://ddnet.tw%s">%s</a>' % (playerWebsite(row[0]), escape(row[0])),
        row[0])

try:
  with open(htmlRanksPath, 'r+') as f:
    lines = []
    endTime = datetime.datetime.now() - datetime.timedelta(weeks=1)
    for line in f:
      [timeStr, content] = line.strip().split('\x1e', 1)
      if parseDatetime(timeStr) > endTime:
        lines.append(line)
  with open(htmlRanksPathTmp, 'w') as f:
      f.writelines(lines)
  os.rename(htmlRanksPathTmp, htmlRanksPath)
except IOError:
  pass

try:
  with open(htmlRanksPath, 'r+') as f, open(feedPathTmp, 'w+') as fatom:
    print >>fatom, """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>DDraceNetwork Top Records</title>
  <link href="http://ddnet.tw/status/records/feed/" rel="self" />
  <link href="http://ddnet.tw/status/" />
  <id>http://ddnet.tw/status/</id>
  <updated>%s</updated>
""" % formatDateExact(datetime.datetime.now())

    for line in reversed(f.readlines()):
      [timeStr, content, title] = line.strip().split('\x1e', 2)
      dt = parseDatetime(timeStr)

      #title = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*/>', '[\g<1>]', content)
      #title = re.sub(r'<a [^>]*>', '', title)
      #title = re.sub(r'</a>', '', title)
      #title = re.sub(r'&amp;', '&', title)

      print >>fatom, """  <entry>
    <updated>%s</updated>
    <title>
      %s
    </title>
    <content type="html">
      %s
    </content>
  </entry>
""" % (formatDateFeedStr(formatDate(dt)), escape(title), escape(content))

    print >>fatom, "</feed>"
  os.rename(feedPathTmp, feedPath)
except IOError:
  pass
