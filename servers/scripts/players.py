#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
import sys
from cgi import escape
from datetime import datetime, timedelta
import cStringIO
import msgpack
#from guppy import hpy

reload(sys)
sys.setdefaultencoding('utf8')

types = None
players = None
maps = None
totalPoints = None
pointsRanks = None
weeklyPointsRanks = None
monthlyPointsRanks = None
teamrankRanks = None
rankRanks = None
serverRanks = None
last = None

def reloadData():
  global types, players, maps, totalPoints, pointsRanks, weeklyPointsRanks, monthlyPointsRanks, teamrankRanks, rankRanks, serverRanks, last
  now = datetime.now()
  if not last or last <= now - timedelta(minutes=20) or (last - timedelta(minutes=1)).minute / 20 != (now - timedelta(minutes=1)).minute / 20:
    with open('%s/players.msgpack' % webDir, 'rb') as inp:
      unpacker = msgpack.Unpacker(inp)
      types = unpacker.unpack()
      maps = unpacker.unpack()
      totalPoints = unpacker.unpack()
      pointsRanks = unpacker.unpack()
      weeklyPointsRanks = unpacker.unpack()
      monthlyPointsRanks = unpacker.unpack()
      teamrankRanks = unpacker.unpack()
      rankRanks = unpacker.unpack()
      serverRanks = unpacker.unpack()
      players = unpacker.unpack()
      last = datetime.now()

def printPersonalResult(name, ranks, player):
  string = '<div class="block2 ladder"><h3>%s</h3>\n<p class="pers-result">' % name

  found = False
  currentPos = 0
  currentRank = 0
  skips = 1
  lastPoints = 0

  for r in ranks:
    currentPos += 1
    if r[1] != lastPoints:
      lastPoints = r[1]
      currentRank += skips
      skips = 1
    else:
      skips += 1

    if r[0] == player:
      string += '%d. with %d points' % (currentRank, r[1])
      found = True
      break

  if not found:
    string += 'Unranked'
  string += '</p></div>'

  return string

def application(env, start_response):
  path = env['PATH_INFO']

  if len(path.split('/')) > 4:
    start_response('404 Not Found', [('Content-Type', 'text/html')])
    with open('%s/404/index.html' % webDir, 'rb') as err:
      return err.read()

  if (not path.endswith("/")) or path.endswith(".html"):
    start_response('301 Moved Permanently', [('Location', path.rstrip('/').rsplit('.html', 1)[0] + "/")])
    return

  name = deslugify2(path.split('/')[2])
  reloadData()
  player = players.get(name)

  if not player:
    start_response('404 Not Found', [('Content-Type', 'text/html')])
    with open('%s/players/index.html' % webDir, 'rb') as err:
      return err.read()

  start_response('200 OK', [('Content-Type', 'text/html')])

  out = cStringIO.StringIO()

  menuText = '<ul>'
  menuText += '<li><a href="#global">Global Ranks for %s</a></li>' % name
  for type in types:
    menuText += '<li><a href="#%s">%s Server</a></li>\n' % (type, type.title())
  menuText += '</ul>'

  print >>out, header("Statistics for %s - DDraceNetwork" % name, menuText, "")

  print >>out, '<div id="global" class="block div-ranks"><h2>Global Ranks for %s</h2>' % name
  print >>out, printPersonalResult("Points (%d total)" % totalPoints, pointsRanks, name)
  print >>out, printPersonalResult("Team Rank", teamrankRanks, name)
  print >>out, printPersonalResult("Rank", rankRanks, name)
  print >>out, '<br/>'
  print >>out, printPersonalResult("Points (last month)", monthlyPointsRanks, name)
  print >>out, printPersonalResult("Points (last week)", weeklyPointsRanks, name)
  print >>out, '<br/></div>'

  for type in types:
    maps2 = maps[type]
    print >>out, '<div id="%s" class="block div-ranks"><h2>%s Server</h2>' % (type, type.title())

    print >>out, printPersonalResult("Points (%d total)" % serverRanks[type][0], serverRanks[type][1], name)
    print >>out, printPersonalResult("Team Rank", serverRanks[type][2], name)
    print >>out, printPersonalResult("Rank", serverRanks[type][3], name)
    print >>out, '<br/>'

    unfinishedString = ""

    tblString = '<table class="spacey"><tr><th>Map</th><th>Points</th><th>Team Rank</th><th>Rank</th><th>Time</th><th>Finishes</th><th>First Finish</th></tr>\n'
    found = False

    for map in maps2:
      normMap = normalizeMapname(map)
      if map in player[0]:
        found = True
        #if player[0][map][4].year > 2014:
        #  print >> sys.stderr, player[0][map][1]
        #  print >> sys.stderr, player[0][map][3]
        #  print >> sys.stderr, "first"
        #  print >> sys.stderr, player[0][map][4]
        #  print >> sys.stderr, name
        #  print >> sys.stderr, map
        #  continue

        tblString += '<tr><td><a href="/ranks/%s/#map-%s">%s</a></td><td class="smallpoints">%d</td><td class="rank">%s</td><td class="rank">%s</td><td class="rank">%s</td><td class="rank">%d</td><td class="rank">%s</td></tr>\n' % (type, escape(normMap), escape(map), player[0][map][2], formatRank(player[0][map][0]), formatRank(player[0][map][1]), escape(formatTime(player[0][map][5])), player[0][map][3], escape(formatDate(datetime.strptime(player[0][map][4], "%Y-%m-%d %H:%M:%S"))))
      else:
        unfinishedString += '<a href="/ranks/%s/#map-%s">%s</a>, ' % (type, escape(normMap), escape(map))

    tblString += '</table>'
    if found:
      print >>out, tblString

    print >>out, '<p>'
    if len(unfinishedString) == 0:
      print >>out, '<strong>All maps on %s finished!</strong>' % type.title()
    else:
      print >>out, '<strong>Unfinished maps</strong>: %s' % unfinishedString[:-2]
    print >>out, '</p></div>'

  print >>out, """  </section>
</article>
</body>
</html>"""

  #h = hpy()
  #print h.heap()

  return out.getvalue()
