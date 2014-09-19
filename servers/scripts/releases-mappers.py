#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
from cgi import escape

reload(sys)
sys.setdefaultencoding('utf8')

def footer():
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
types = sys.argv[1:]

f = open("releases")
releases = []
for line in f:
  words = line.rstrip('\n').split('\t')
  releases.append(tuple(words))

mappers = {}

for x in releases:
  date, server, y = x
  try:
    stars, originalMapName, mapperName = y.split('|')
  except ValueError:
    stars, originalMapName = y.split('|')
    mapperName = ""

  for name in splitMappers(mapperName):
    if name not in mappers:
      mappers[name] = {}
    if server not in mappers[name]:
      mappers[name][server] = []
    stars = int(stars)
    mappers[name][server].append((date, server, stars, originalMapName, mapperName))

for mapper, servers in mappers.iteritems():
  serversString = ""

  filename = "%s/mappers/%s/index.html" % (webDir, slugify2(u'%s' % mapper))
  tmpname = "%s/mappers/%s/index.tmp" % (webDir, slugify2(u'%s' % mapper))
  directory = os.path.dirname(filename)
  if not os.path.exists(directory):
    os.makedirs(directory)
  tf = open(tmpname, 'w')

  menuText = '<ul>\n'
  for type in types:
    if type in servers:
      menuText += '<li><a href="/ranks/%s/">%s Server</a></li>\n' % (type, type.title())
  menuText += '</ul>'
  print >>tf, header('%s - Mapper Profile - DDraceNetwork' % mapper, menuText, '')

  for type in types:
    mapsString = '<div id="novice" class="longblock div-ranks">\n'
    mapsString += '<div class="block7"><h2>%s Server</h2></div><br/>\n' % type.title()
    if type not in servers:
      continue

    for (date, server, stars, originalMapName, mapperName) in servers[type]:

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

      mapsString += u'<div class="blockreleases release" id="map-%s"><h3 class="inline">%s</h3><br/><h3 class="inline"><a href="/ranks/%s/#map-%s">%s</a></h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/maps/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" /></a>%s<br/></div>\n' % (escape(mapName), date, server, escape(normalizeMapname(originalMapName)), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(server, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo)

    mapsString += '<span class="stretch"></span></div>\n'
    serversString += mapsString
    serversString += '</div>\n'

  print >>tf, '<div id="global" class="block"><h2>Mapper Profile: %s</h2><br/></div>' % mapper
  print >>tf, serversString
  print >>tf, footer()

  tf.close()
  os.rename(tmpname, filename)
