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
  %s
  </body>
</html>""" % printDateTimeScript()

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

mapsStrings = ['']
currentMapCount = 0

mapsJsonT = []
for x in releases:
  jsonT = OrderedDict()

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
  slugifiedMapName = slugify2(originalMapName)

  jsonT['name'] = originalMapName
  jsonT['website'] = 'https://ddnet.tw/maps/%s' % slugifiedMapName
  jsonT['thumbnail'] = 'https://ddnet.tw/ranks/maps/%s.png' % mapName
  jsonT['web_preview'] = 'https://ddnet.tw/mappreview/?map=%s' % quote_plus(originalMapName)
  jsonT['type'] = server
  jsonT['points'] = globalPoints(server, stars)
  jsonT['difficulty'] = stars
  jsonT['mapper'] = mapperName
  jsonT['release'] = date

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

      jsonT['width'] = width
      jsonT['height'] = height
      jsonT['tiles'] = sorted(tiles.keys(), key=lambda i: order(i))
  except IOError:
    pass

  mapsJsonT.append(jsonT)

  # paginate
  if currentMapCount >= 60:
    mapsStrings.append('')
    currentMapCount = 0
  currentMapCount += 1

  dateWithTz = escape(formatDateTimeStrTz(date))
  mapsStrings[-1] += u'<div class="blockreleases release" id="map-%s"><h2 class="inline"><a href="/ranks/%s/">%s Server</a></h2><br/><h3 class="inline" data-type="date" data-date="%s" data-datefmt="datetime">%s</h3><br/><h3 class="inline"><a href="%s">%s</a></h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/mappreview/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/></p></div>\n' % (escape(mapName), server.lower(), server, dateWithTz, date, mapWebsite(originalMapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(server, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo)

for i, mapsString in enumerate(mapsStrings):
  if i == 0:
    filename = '%s/releases/index.html' % webDir
    tmpname = '%s/releases/index.%d.tmp' % (webDir, os.getpid())
  else:
    filename = '%s/releases/%d/index.html' % (webDir, i+1)
    tmpname = '%s/releases/%d/index.%d.tmp' % (webDir, i+1, os.getpid())

  directory = os.path.dirname(filename)
  if not os.path.exists(directory):
    os.makedirs(directory)

  with open(tmpname, 'w') as tf:
    print >>tf, header("Map Releases (%d/%d) - DDraceNetwork" % (i+1, len(mapsStrings)), "", "")
    print >>tf, '<div id="global" class="block">'
    print >>tf, '<div class="right"><form id="mapform" action="/maps/" method="get"><input name="map" class="typeahead" type="text" placeholder="Map search"><input type="submit" value="Map search" style="position: absolute; left: -9999px"></form></div>'
    print >>tf, '<h2>Map Releases (%d/%d)</h2><br/>' % (i+1, len(mapsStrings))
    print >>tf, '<script src="/jquery.js" type="text/javascript"></script>'
    print >>tf, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
    print >>tf, '<script src="/mapsearch.js" type="text/javascript"></script>'
    print >>tf, '<a href="feed/"><img width="36" src="/feed.svg"/></a> You can subscribe to the feed to get updated about new map releases.<br>'
    print >>tf, '<a href="maps.json"><img width="36" src="/json.svg"/></a> All map release infos are also available in JSON format.'
    print >>tf, '<p>Planned Map Releases are listed on <a href="https://discordapp.com/invite/85Vavs">Discord</a>. All DDNet maps can be download from <a href="https://github.com/ddnet/ddnet-maps">GitHub</a>, <a href="https://maps.ddnet.tw/compilations/">our compilations</a> or <a href="https://maps.ddnet.tw/">as single files</a>.</p>'
    print >>tf, '<div class="flex-container">\n'
    print >>tf, mapsString
    print >>tf, '</div>\n'
    print >>tf, '<span class="stretch"></span></div>'

    if len(mapsStrings) > 1:
      print >>tf, '<div class="longblock div-ranks"><h3 style="text-align: center;">'
      for i in range(len(mapsStrings)):
        if i == 0:
          link = '/releases/'
        else:
          link = '/releases/%d/' % (i+1)
          print >>tf, ' '
        print >>tf, '<a href="%s">%d</a>' % (link, i+1)
      print >>tf, '</h3></div>'

    print >>tf, printFooter()
  os.rename(tmpname, filename)

filename = '%s/releases/maps.json' % webDir
tmpname = '%s/releases/maps.%d.tmp' % (webDir, os.getpid())
with open(tmpname, 'w') as tf:
    json.dump(mapsJsonT, tf)
os.rename(tmpname, filename)
