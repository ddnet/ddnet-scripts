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

menuText = '<ul>'
for tile in all_tiles:
  menuText += '<li><a href="/tiles/%s/">%s</a></li>' % (tile, description(tile))
menuText += '</ul>'

con = mysqlConnect()

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")
  for tile in all_tiles:
    mapsStrings = ['']
    currentMapCount = 0

    cur.execute("select record_maps.Map, Server, Mapper, Stars, DATE_FORMAT(Timestamp, '%%Y-%%m-%%d %%H:%%i') from record_mapinfo inner join record_maps on record_mapinfo.Map = record_maps.Map where %s = True order by Timestamp desc;" % tile)
    rows = cur.fetchall()
    for row in rows:
      originalMapName = row[0]
      mapName = normalizeMapname(originalMapName)
      server = row[1]
      mapperName = row[2]
      stars = row[3]
      date = row[4]

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
          ts = unpacker.unpack()

          formattedMapName = '<span title="Map size: %dx%d">%s</span>' % (width, height, escape(originalMapName))

          mbMapInfo = "<br/>"
          for t in sorted(ts.keys(), key=lambda i:order(i)):
            mbMapInfo += tileHtml(t)
      except IOError:
        pass

      # paginate
      if currentMapCount >= 60:
        mapsStrings.append('')
        currentMapCount = 0
      currentMapCount += 1

      mapsStrings[-1] += u'<div class="blockreleases release" id="map-%s"><h2 class="inline"><a href="/ranks/%s/">%s Server</a></h2><br/><h3 class="inline">%s</h3><br/><h3 class="inline"><a href="%s">%s</a></h3><p class="inline">%s</p><p>Difficulty: %s, Points: %d<br/><a href="/mappreview/?map=%s"><img class="screenshot" alt="Screenshot" src="/ranks/maps/%s.png" width="360" height="225" /></a>%s<br/></p></div>\n' % (escape(mapName), server.lower(), server, date, mapWebsite(originalMapName), formattedMapName, mbMapperName, escape(renderStars(stars)), globalPoints(server, stars), quote_plus(originalMapName), escape(mapName), mbMapInfo)

    for i, mapsString in enumerate(mapsStrings):
      if i == 0:
        filename = '%s/tiles/%s/index.html' % (webDir, tile)
        tmpname = '%s/tiles/%s/index.%d.tmp' % (webDir, tile, os.getpid())
      else:
        filename = '%s/tiles/%s/%d/index.html' % (webDir, tile, i+1)
        tmpname = '%s/tiles/%s/%d/index.%d.tmp' % (webDir, tile, i+1, os.getpid())

      directory = os.path.dirname(filename)
      if not os.path.exists(directory):
        os.makedirs(directory)

      tf = open(tmpname, 'w')

      print >>tf, header("Maps with %s Tile (%d/%d) - DDraceNetwork" % (description(tile), i+1, len(mapsStrings)), menuText, "")
      print >>tf, '<div id="global" class="block">'
      print >>tf, '<div class="right"><form id="mapform" action="/maps/" method="get"><input name="map" class="typeahead" type="text" placeholder="Map search"><input type="submit" value="Map search" style="position: absolute; left: -9999px"></form></div>'
      print >>tf, '<h2>Maps with %s Tile (%d/%d)</h2><br/>' % (description(tile), i+1, len(mapsStrings))
      print >>tf, '<script src="/jquery.js" type="text/javascript"></script>'
      print >>tf, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
      print >>tf, '<script src="/mapsearch.js" type="text/javascript"></script>'
      print >>tf, mapsString
      print >>tf, '<span class="stretch"></span></div>'

      if len(mapsStrings) > 1:
        print >>tf, '<div class="longblock div-ranks"><h3 style="text-align: center;">'
        for i in range(len(mapsStrings)):
          if i == 0:
            link = '/tiles/%s/' % tile
          else:
            link = '/tiles/%s/%d/' % (tile, i+1)
            print >>tf, ' '
          print >>tf, '<a href="%s">%d</a>' % (link, i+1)
        print >>tf, '</h3></div>'

      print >>tf, printFooter()

      tf.close()
      os.rename(tmpname, filename)

#filename = '%s/tiles/index.html' % webDir
#tmpname = '%s/tiles/index.%d.tmp' % (webDir, os.getpid())
#tf = open(tmpname, 'w')
#
#print >>tf, header("Maps with %s Tiles (%d/%d) - DDraceNetwork" % (description(tile), i+1, len(mapsStrings)), "", "")
#print >>tf, '<div id="global" class="block">'
#print >>tf, '<div class="right"><form id="mapform" action="/maps/" method="get"><input name="map" class="typeahead" type="text" placeholder="Map search"><input type="submit" value="Map search" style="position: absolute; left: -9999px"></form></div>'
#print >>tf, '<h2>Maps with %s Tile (%d/%d)</h2><br/>' % (description(tile), i+1, len(mapsStrings))
