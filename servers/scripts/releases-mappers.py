#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
import os
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
    if name == '':
      name = 'Unknown Mapper'
    if name not in mappers:
      mappers[name] = {}
    if server not in mappers[name]:
      mappers[name][server] = []
    stars = int(stars)
    mappers[name][server].append((date, server, stars, originalMapName, mapperName))

for mapper, servers in mappers.iteritems():
  serversString = ""

  filename = "%s/mappers/%s/index.html" % (webDir, slugify2(u'%s' % mapper))
  tmpname = "%s/mappers/%s/index.%d.tmp" % (webDir, slugify2(u'%s' % mapper), os.getpid())
  directory = os.path.dirname(filename)
  if not os.path.exists(directory):
    os.makedirs(directory)
  tf = open(tmpname, 'w')

  menuText = '<ul>\n'
  menuText += '<li><a href="/mappers/">All Mappers</a></li>\n'
  menuText += '<li><a href="#global">Mapper Profile: %s</a></li>\n' % escape(mapper)
  for type in types:
    if type in servers:
      menuText += '<li><a href="#%s">%s Server</a></li>\n' % (type, type)
  menuText += '</ul>'
  print >>tf, header('%s - Mapper Profile - DDraceNetwork' % escape(mapper), menuText, '')

  for type in types:
    mapsString = '<div id="%s" class="longblock div-ranks">\n' % type
    mapsString += '<div class="block7"><h2>%s Server</h2></div><br/>\n' % type
    if type not in servers:
      continue

    mapsString += '<div class="flex-container">\n'

    for (date, server, stars, originalMapName, mapperName) in servers[type]:
      if date == "2013-10-14 19:40":
        date = ""

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

      mapsString += u'<div class="blockreleases release" id="map-%s"><h3 class="inline">%s</h3><br/><h3 class="inline"><a href="%s">%s</a></h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/mappreview/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/></p></div>\n' % (escape(mapName), date, mapWebsite(originalMapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(server, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo)

    mapsString += '</div>\n'
    mapsString += '<span class="stretch"></span></div>\n'
    serversString += mapsString
    serversString += '</div>\n'

  print >>tf, '<div id="global" class="block"><h2>Mapper Profile: %s</h2><br/></div>' % escape(mapper)
  print >>tf, serversString
  print >>tf, footer()

  tf.close()
  os.rename(tmpname, filename)

print header('Mappers - DDraceNetwork', '', '')
print '<div id="global" class="longblock"><h2>Mappers</h2><p>%d mappers total:</p>' % len(mappers)

for name in sorted(mappers.iterkeys(), key=str.lower):
  servers = mappers[name]
  tmp = ''
  total = 0
  for type in types:
    if type in servers:
      maps = servers[type]
      if len(tmp):
        tmp += ', '
      tmp += type + ': ' + str(len(maps))
      total += len(maps)
  print '<p><a href="%s">%s</a>: %d map%s (%s)</p>' % (mapperWebsite(name), escape(name), total, '' if total == 1 else 's', tmp)

print '</div>'
