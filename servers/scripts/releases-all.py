#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
from cgi import escape

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

menuText = '<ul>\n'
menuText += '<li><a href="/releases/">Recent Releases</a></li>\n'
menuText += '<li><a href="/releases/all/">All Releases</a></li>\n'
menuText += '</ul>'
print header("All Map Releases - DDraceNetwork", menuText, "")

f = open("releases")
releases = []
for line in f:
  words = line.rstrip('\n').split('\t')
  releases.append(tuple(words))

serversString = ""
mapsString = ""

for x in releases:
  date, server, y = x
  try:
    stars, originalMapName, mapperName = y.split('|')
  except ValueError:
    stars, originalMapName = y.split('|')
    mapperName = ""

  if date == "2013-10-14 19:40":
    date = ""

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

      formattedMapName = '<span title="%dx%d">%s</span>' % (width, height, escape(originalMapName))

      mbMapInfo = "<br/>"
      for tile in sorted(tiles.keys(), key=lambda i:order(i)):
        mbMapInfo += '<span title="%s"><img alt="%s" src="/tiles/%s.png" width="32" height="32"/></span> ' % (description(tile), description(tile), tile)
  except IOError:
    pass

  mapsString += u'<div class="blockreleases release" id="map-%s"><h2 class="inline"><a href="/ranks/%s">%s Server</a></h2><br/><h3 class="inline">%s</h3><br/><h3 class="inline"><a href="/ranks/%s/#map-%s">%s</a></h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/maps/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/></p></div>\n' % (escape(mapName), server.lower(), server, date, server.lower(), escape(normalizeMapname(originalMapName)), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(server, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo)

serversString += mapsString
serversString += '<span class="stretch"></span></div>\n'

print '<div id="global" class="block"><h2>All Map Releases</h2><br/>'
print '<a href="feed/"><img width="36" src="/feed.svg"/></a> You can subscribe to the feed to get updated about new map releases'
print '<p>Planned Map Releases are listed on <a href="https://discordapp.com/invite/85Vavs">Discord</a>. All DDNet maps can be download from <a href="https://github.com/ddnet/ddnet-maps">GitHub</a>, <a href="https://maps.ddnet.tw/compilations/">our compilations</a> or <a href="https://maps.ddnet.tw/">as single files</a>.</p>'
print serversString
printFooter()
