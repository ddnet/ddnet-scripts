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

f = open("releases")
releases = []
for line in f:
  words = line.rstrip('\n').split('\t')
  releases.append(tuple(words))

with open('/home/teeworlds/servers/all-types', 'r') as f:
  types = [None] + f.read().split()

menuText = '<ul>\n'
for curType in types:
  if curType:
    menuText += '<li><a href="/releases/%s/">%s Server</a></li>\n' % (curType.lower(), curType)
  else:
    menuText += '<li><a href="/releases/">All Releases</a></li>\n'
menuText += '</ul>'

for curType in types:
  mapsStrings = ['']
  currentMapCount = 0

  mapsJsonT = []

  for x in releases:
    jsonT = OrderedDict()

    date, server, y = x

    if curType and server != curType:
      continue

    try:
      stars, originalMapName, mapperName = y.split('|')
    except ValueError:
      stars, originalMapName = y.split('|')
      mapperName = ""

    if date == "2013-10-14 19:40":
      date = ""

    stars = int(stars)

    mapName = normalizeMapname(originalMapName)
    slugifiedMapName = slugify2(u'%s' % originalMapName)

    jsonT['name'] = originalMapName
    jsonT['website'] = 'https://ddnet.org/maps/%s' % slugifiedMapName
    jsonT['thumbnail'] = 'https://ddnet.org/ranks/maps/%s.png' % mapName
    jsonT['web_preview'] = 'https://ddnet.org/mappreview/?map=%s' % quote_plus(originalMapName)
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
    serverString = '' if curType else '<h2 class="inline"><a href="/ranks/%s/">%s Server</a></h2><br/>' % (server.lower(), server)
    mapsStrings[-1] += u'<div class="blockreleases release" id="map-%s">%s<h3 class="inline" data-type="date" data-date="%s" data-datefmt="datetime">%s</h3><br/><h3 class="inline"><a href="%s">%s</a></h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/mappreview/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/></p></div>\n' % (escape(mapName), serverString, dateWithTz, date, mapWebsite(originalMapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(server, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo)

  serverDir = '%s/releases/%s' % (webDir, curType.lower()) if curType else '%s/releases' % webDir
  if not os.path.exists(serverDir):
    os.makedirs(serverDir)
  for i, mapsString in enumerate(mapsStrings):
    if i == 0:
      filename = '%s/index.html' % serverDir
      tmpname = '%s/index.%d.tmp' % (serverDir, os.getpid())
    else:
      filename = '%s/%d/index.html' % (serverDir, i+1)
      tmpname = '%s/%d/index.%d.tmp' % (serverDir, i+1, os.getpid())

    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
      os.makedirs(directory)

    with open(tmpname, 'w') as tf:
      if curType:
        print >>tf, header("%s Server Map Releases (%d/%d) - DDraceNetwork" % (curType, i+1, len(mapsStrings)), menuText, "")
      else:
        print >>tf, header("Map Releases (%d/%d) - DDraceNetwork" % (i+1, len(mapsStrings)), menuText, "")
      print >>tf, '<div id="global" class="block">'
      print >>tf, '<div class="right"><form id="mapform" action="/maps/" method="get"><input name="map" class="typeahead" type="text" placeholder="Map search"><input type="submit" value="Map search" style="position: absolute; left: -9999px"></form><br><form id="mapperform" action="/maps/" method="get"><input name="mapper" class="typeahead" type="text" placeholder="Mapper search"><input type="submit" value="Mapper search" style="position: absolute; left: -9999px"></form></div>'
      if curType:
        print >>tf, '<h2>%s Server Map Releases (%d/%d)</h2><br/>' % (curType, i+1, len(mapsStrings))
      else:
        print >>tf, '<h2>Map Releases (%d/%d)</h2><br/>' % (i+1, len(mapsStrings))
      print >>tf, '<script src="/jquery.js" type="text/javascript"></script>'
      print >>tf, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
      print >>tf, '<script src="/mapsearch.js" type="text/javascript"></script>'
      print >>tf, '<script src="/mappersearch.js" type="text/javascript"></script>'
      if not curType:
        print >>tf, '<a href="/releases/feed/"><img width="36" src="/feed.svg"/></a> You can subscribe to the feed to get updated about new map releases.<br>'
      if curType:
        print >>tf, '<a href="/releases/%s/maps.json"><img width="36" src="/json.svg"/></a> %s map release infos are also available in JSON format.' % (curType.lower(), curType)
      else:
        print >>tf, '<a href="/releases/maps.json"><img width="36" src="/json.svg"/></a> All map release infos are also available in JSON format.'
      print >>tf, '<p>Planned Map Releases are listed on <a href="https://discordapp.com/invite/85Vavs">Discord</a>. All DDNet maps can be download from <a href="https://github.com/ddnet/ddnet-maps">GitHub</a>, <a href="https://maps.ddnet.org/compilations/">our compilations</a> or <a href="https://maps.ddnet.org/">as single files</a>.</p>'
      print >>tf, '<div class="flex-container">\n'
      print >>tf, mapsString
      print >>tf, '</div>\n'
      print >>tf, '<span class="stretch"></span></div>'

      if len(mapsStrings) > 1:
        print >>tf, '<div class="longblock div-ranks"><h3 style="text-align: center;">'
        for i in range(len(mapsStrings)):
          if i == 0:
            if curType:
              link = '/releases/%s/' % curType.lower()
            else:
              link = '/releases/'
          else:
            if curType:
              link = '/releases/%s/%d/' % (curType.lower(), i+1)
            else:
              link = '/releases/%d/' % (i+1)
            print >>tf, ' '
          print >>tf, '<a href="%s">%d</a>' % (link, i+1)
        print >>tf, '</h3></div>'

      print >>tf, printFooter()
    os.rename(tmpname, filename)

  filename = '%s/maps.json' % serverDir
  tmpname = '%s/maps.%d.tmp' % (serverDir, os.getpid())
  with open(tmpname, 'w') as tf:
      json.dump(mapsJsonT, tf)
  os.rename(tmpname, filename)
