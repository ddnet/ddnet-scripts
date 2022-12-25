#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
from cgi import escape
import os

reload(sys)
sys.setdefaultencoding('utf8')

def printFooter():
  return """
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

f = open("tournaments")
tournaments = []
for line in f:
  words = line.rstrip('\n').split('|')
  tournaments.append(tuple(words))

mapsString = ''
currentMapCount = 0

for x in tournaments:
  date, tournament, link, server, stars, originalMapName, mapperName = x

  stars = int(stars)

  mapName = normalizeMapname(originalMapName)

  if not mapperName:
    mbMapperName = ""
  else:
    names = splitMappers(mapperName)
    newNames = []
    for name in names:
      newNames.append('<a href="%s">%s</a>' % (mapperWebsite(name), escape(name)))

    mbMapperName = "<strong>by %s</strong><br/>" % makeAndString(newNames)

  formattedMapName = escape(originalMapName)
  mbMapInfo = ""
  try:
    with open('maps/%s.msgpack' % originalMapName, 'rb') as inp:
      unpacker = msgpack.Unpacker(inp)
      width = unpacker.unpack()
      height = unpacker.unpack()
      tiles = unpacker.unpack()

      formattedMapName = '<span title="Map size: %dx%d">%s</span>' % (width, height, escape(originalMapName))

      mbMapInfo = "<br/>"
      for tile in sorted(tiles.keys(), key=lambda i:order(i)):
        mbMapInfo += tileHtml(tile)
  except IOError:
    pass

  serverString = "" if "Advent" in tournament else ": %s Server" % server
  mapsString += u'<div class="blockreleases release" id="map-%s"><h2 class="inline"><a href="%s/">%s%s</a></h2><br/><h3 class="inline">%s</h3><br/><h3 class="inline"><a href="%s">%s</a></h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="%s/"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/></p></div>\n' % (escape(mapName), link, tournament, serverString, date, mapWebsite(originalMapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(server, stars), link, escape(mapName), mbMapInfo)

filename = '%s/tournaments/index.html' % webDir
tmpname = '%s/tournaments/index.%d.tmp' % (webDir, os.getpid())

directory = os.path.dirname(filename)
if not os.path.exists(directory):
  os.makedirs(directory)

tf = open(tmpname, 'w')

print >>tf, header("Tournaments - DDraceNetwork", "", "")
print >>tf, '<div id="global" class="block">'
print >>tf, '<div class="right"><form id="mapform" action="/maps/" method="get"><input name="map" class="typeahead" type="text" placeholder="Map search"><input type="submit" value="Map search" style="position: absolute; left: -9999px"></form></div>'
print >>tf, '<h2>Tournaments</h2><br/>'
print >>tf, '<script src="/jquery.js" type="text/javascript"></script>'
print >>tf, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
print >>tf, '<script src="/mapsearch.js" type="text/javascript"></script>'
print >>tf, mapsString
print >>tf, '<span class="stretch"></span></div>'

print >>tf, printFooter()

tf.close()
os.rename(tmpname, filename)
