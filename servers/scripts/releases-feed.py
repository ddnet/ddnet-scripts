#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
from cgi import escape
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf8')

def printFooter():
  print """
  </section>
  </article>
  </body>
</html>"""

rankLadder = {}
teamrankLadder = {}
pointsLadder = {}
serversString = ""
players = {}
maps = {}
totalPoints = 0
serverRanks = {}

f = open("releases")
releases = []
for line in f:
  words = line.rstrip('\n').split('\t')
  releases.append(tuple(words))
  if len(releases) >= 24:
    break

print """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>DDraceNetwork Map Releases</title>
  <link href="http://ddnet.org/releases/feed/" rel="self" />
  <link href="http://ddnet.org/releases/" />
  <id>http://ddnet.org/releases/</id>
  <updated>%s</updated>
""" % formatDateFeedStr(releases[0][0])

for x in releases:
  date, server, y = x
  try:
    stars, originalMapName, mapperName = y.split('|')
  except ValueError:
    stars, originalMapName = y.split('|')
    mapperName = ""

  stars = int(stars)

  mapName = normalizeMapname(originalMapName)

  if not mapperName:
    mbMapperName = ""
    mbRawMapperName = ""
    rawMapperName = "Unknown Mapper"
  else:
    names = splitMappers(mapperName)
    newNames = []
    newRawNames = []
    for name in names:
      newNames.append('<a href="%s">%s</a>' % (mapperWebsite(name), escape(name)))
      newRawNames.append(escape(name))

    mbMapperName = "by %s" % makeAndString(newNames, ampersand = "&amp;")
    mbRawMapperName = " by %s" % makeAndString(newRawNames, ampersand = "&amp;")
    rawMapperName = makeAndString(newRawNames, ampersand = "&amp;")

  formattedMapName = escape(originalMapName)
  mbMapInfo = ""
  try:
    with open('maps/%s.msgpack' % originalMapName, 'rb') as inp:
      unpacker = msgpack.Unpacker(inp)
      width = unpacker.unpack()
      height = unpacker.unpack()
      tiles = unpacker.unpack()

      formattedMapName = '<span title="Map size: %dx%d">%s</span>' % (width, height, escape(originalMapName))

      for tile in sorted(tiles.keys(), key=lambda i:order(i)):
        mbMapInfo += tileHtml(tile)
  except IOError:
    pass

  mapsString = u'<p>New map <a href="%s">%s</a> %s released on the <a href="/ranks/%s/">%s Server</a></p><p>Difficulty: %s, Points: %d</p><p><a href="/mappreview/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a></p><p>%s</p>' % (mapWebsite(originalMapName), formattedMapName, mbMapperName, server.lower(), server, escape(renderStars(stars)), globalPoints(server, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo)
  print """  <entry>
    <title>[%s] %s%s</title>
    <link href="%s" />
    <id>urn:map:%s</id>
    <updated>%s</updated>
    <author>
      <name>%s</name>
    </author>
    <content type="xhtml">
      <div xmlns="http://www.w3.org/1999/xhtml">
        %s
      </div>
    </content>
  </entry>
""" % (server, escape(originalMapName), mbRawMapperName, mapWebsite(originalMapName), escape(mapName), formatDateFeedStr(date), rawMapperName, mapsString)

print "</feed>"
