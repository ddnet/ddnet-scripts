#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
import sys
from cgi import escape
from datetime import datetime, timedelta
import cStringIO
import msgpack
from operator import itemgetter
import urllib
import json
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

con = mysqlConnect()
con.autocommit(True)

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8';")

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

  def globalRanks(name, player):
    out = cStringIO.StringIO()

    print >>out, '<div class="block7">'
    print >>out, printPersonalResult("Points (%d total)" % totalPoints, pointsRanks, name)
    print >>out, printPersonalResult("Team Rank", teamrankRanks, name)
    print >>out, printPersonalResult("Rank", rankRanks, name)
    print >>out, '<br/>'
    print >>out, printPersonalResult("Points (last month)", monthlyPointsRanks, name)
    print >>out, printPersonalResult("Points (last week)", weeklyPointsRanks, name)

    try:
      favServer = max(player[1].iteritems(), key=itemgetter(1))[0]
      if favServer == None:
        favServer = 'UNK'
    except:
      favServer = 'UNK'

    print >>out, '<div class="block2 ladder"><h3>Favorite Server</h3>\n<p class="pers-result"><img src="/countryflags/%s.png" alt="%s" height="20" /></p></div>' % (favServer, favServer)
    print >>out, '</div>'

    return out.getvalue()

  def lastFinishes(name):
    out = cStringIO.StringIO()

    print >>out, '<div class="block6 ladder"><h3>Last Finishes</h3><table class="tight">'

    cur.execute("select Timestamp, Map, Time from record_race where Name = '%s' order by Timestamp desc limit 10;" % con.escape_string(name))
    rows = cur.fetchall()

    for row in rows:
      type = ''
      for t in types:
        if row[1] in maps[t]:
          type = t
          break

      print >> out, '<tr><td>%s: <a href="/ranks/%s/#map-%s">%s</a> (%s)</td></tr>' % (escape(formatDate(row[0])), type, escape(normalizeMapname(row[1])), escape(row[1]), escape(formatTime(row[2])))

    print >>out, '</table></div>'

    return out.getvalue()

  def comparison(namePlayers):
    out = cStringIO.StringIO()

    orText = ''
    for (name, player) in namePlayers[:-1]:
      if orText != '':
        orText += ', '
      orText += escape(name)
    orText += ' or ' + escape(namePlayers[-1][0])

    andText = ''
    for (name, player) in namePlayers[:-1]:
      if andText != '':
        andText += ', '
      andText += escape(name)
    andText += ' and ' + escape(namePlayers[-1][0])

    tableText = ''
    for (name, player) in namePlayers:
      tableText += '<th>' + escape(name) + '</th>'

    menuText = '<ul>'
    menuText += '<li><a href="#global">Comparison of %s</a></li>' % andText
    for type in types:
      menuText += '<li><a href="#%s">%s Server</a></li>\n' % (type, type.title())
    menuText += '</ul>'

    print >>out, header("Comparison of %s - DDraceNetwork" % andText, menuText, "")

    hiddenFields = ''
    for (name, player) in namePlayers:
      hiddenFields += '<input type="hidden" name="player" value="%s">' % escape(name)

    print >>out, '<div id="global" class="block div-ranks">'
    print >>out, '<div id="remote" class="right"><form id="playerform" action="/compare/" method="get">%s<input name="player" class="typeahead" type="text" placeholder="Add to comparison"><input type="submit" value="Add to comparison" style="position: absolute; left: -9999px"></form></div>' % hiddenFields
    print >>out, '<script src="/jquery.js" type="text/javascript"></script>'
    print >>out, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
    print >>out, '<script src="/playersearch.js" type="text/javascript"></script>'
    for (name, player) in namePlayers:
      print >>out, '<div class="block7"><h2>Global Ranks for <a href="%s">%s</a></h2></div><br/>' % (playerWebsite(name), escape(name))
      print >>out, globalRanks(name, player)
      print >>out, '<br/>'
    print >>out, '</div>'

    for type in types:
      maps2 = maps[type]
      print >>out, '<div id="%s" class="block div-ranks"><h2>%s Server</h2>' % (type, type.title())

      for (name, player) in namePlayers:
        print >>out, '<div class="block2 ladder"><h2>%s</h2></div>' % name
        print >>out, printPersonalResult("Points (%d total)" % serverRanks[type][0], serverRanks[type][1], name)
        print >>out, printPersonalResult("Team Rank", serverRanks[type][2], name)
        print >>out, printPersonalResult("Rank", serverRanks[type][3], name)
        print >>out, '<br/>'

      unfinishedString = ""

      tblString = '<table class="spacey"><tr><th>Map</th><th>Points</th><th colspan="%d">Time</th><th colspan="%d">Rank</th><th colspan="%d">Team Rank</th></tr><tr><th></th><th></th>%s%s%s</tr>\n' % (len(namePlayers), len(namePlayers), len(namePlayers), tableText, tableText, tableText)
      found = False

      for map in maps2:
        normMap = normalizeMapname(map)
        tmpStrings = [['<td class="rank verticalLine"></td>'] * 3]
        for i in range(len(namePlayers) - 1):
          tmpStrings.append(['<td class="rank"></td>'] * 3)
        i = 0
        foundNow = False
        for (name, player) in namePlayers:
          if map in player[0]:
            found = True
            foundNow = True
            if name == namePlayers[0][0]:
              tmpStrings[i][0] = '<td class="rank verticalLine">%s</td>' % escape(formatTime(player[0][map][5]))
              tmpStrings[i][1] = '<td class="rank verticalLine">%s</td>' % formatRank(player[0][map][1])
              tmpStrings[i][2] = '<td class="rank verticalLine">%s</td>' % formatRank(player[0][map][0])
            else:
              tmpStrings[i][0] = '<td class="rank">%s</td>' % escape(formatTime(player[0][map][5]))
              tmpStrings[i][1] = '<td class="rank">%s</td>' % formatRank(player[0][map][1])
              tmpStrings[i][2] = '<td class="rank">%s</td>' % formatRank(player[0][map][0])
            points = player[0][map][2]
          i += 1

        if foundNow:
          tblString += '<tr><td><a href="/ranks/%s/#map-%s">%s</a></td><td class="smallpoints">%d</td>' % (type, escape(normMap), escape(map), points)
          for i in range(len(namePlayers)):
            tblString += tmpStrings[i][0]
          for i in range(len(namePlayers)):
            tblString += tmpStrings[i][1]
          for i in range(len(namePlayers)):
            tblString += tmpStrings[i][2]
          tblString += '</tr>\n'
        else:
          unfinishedString += '<a href="/ranks/%s/#map-%s">%s</a>, ' % (type, escape(normMap), escape(map))

      tblString += '</table>'
      if found:
        print >>out, tblString

      print >>out, '<p>'
      if len(unfinishedString) == 0:
        print >>out, '<strong>All maps on %s finished by %s!</strong>' % (type.title(), orText)
      else:
        print >>out, '<strong>Maps unfinished by %s</strong>: %s' % (andText, unfinishedString[:-2])
      print >>out, '</p></div>'

    print >>out, """  </section>
  </article>
  </body>
  </html>"""

    #h = hpy()
    #print h.heap()

    return out.getvalue()

  def application(env, start_response):
    path = env['PATH_INFO']

    if path.startswith('/compare/'):
      if len(path.split('/')) > 20:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        with open('%s/404/index.html' % webDir, 'rb') as err:
          return err.read()

      if (not path.endswith("/")) or path.endswith(".html"):
        start_response('301 Moved Permanently', [('Location', path.rstrip('/').rsplit('.html', 1)[0] + "/")])
        return ''

      reloadData()

      namePlayers = []
      for n in path.split('/')[2:-1]:
        name = deslugify2(n)
        player = players.get(name)

        if not player:
          start_response('404 Not Found', [('Content-Type', 'text/html')])
          return "Player %s not found" % escape(name)

        namePlayers.append((name, player))

      if len(namePlayers) == 0:
        qs = env['QUERY_STRING'].split('&player=')
        if not qs[0].startswith('player='):
          start_response('404 Not Found', [('Content-Type', 'text/html')])
          with open('%s/404/index.html' % webDir, 'rb') as err:
            return err.read()
        qs[0] = qs[0][7:]

        newPath = '/compare/'
        for q in qs:
          newPath += slugify2(u'%s' % urllib.unquote_plus(q)).encode('utf-8') + '/'
        start_response('301 Moved Permanently', [('Location', newPath)])
        return ''

      start_response('200 OK', [('Content-Type', 'text/html')])
      return comparison(namePlayers)

    if path == '/players/':
      qs = env['QUERY_STRING']

      if len(qs) > 0 and qs.startswith('player='):
        q = qs[7:]

        newPath = '/players/' + slugify2(u'%s' % urllib.unquote_plus(q)).encode('utf-8') + '/'
        start_response('301 Moved Permanently', [('Location', newPath)])
        return ''

      if len(qs) > 0 and qs.startswith('query='):
        q = urllib.unquote_plus(qs[6:])
        ql = q.lower()

        jsonT = []
        reloadData()
        for r in pointsRanks:
          if r[0].lower().startswith(ql):
            jsonT.append({'name': r[0], 'points': r[1]})
            if len(jsonT) > 10:
              break

        for r in pointsRanks:
          if ql in r[0].lower() and {'name': r[0], 'points': r[1]} not in jsonT:
            jsonT.append({'name': r[0], 'points': r[1]})
            if len(jsonT) > 10:
              break

        start_response('200 OK', [('Content-Type', 'application/json')])
        return json.dumps(jsonT)

      start_response('200 OK', [('Content-Type', 'text/html')])
      with open('%s/players/index.html' % webDir, 'rb') as err:
        return err.read()

    if len(path.split('/')) > 4:
      start_response('404 Not Found', [('Content-Type', 'text/html')])
      with open('%s/404/index.html' % webDir, 'rb') as err:
        return err.read()

    if (not path.endswith("/")) or path.endswith(".html"):
      start_response('301 Moved Permanently', [('Location', path.rstrip('/').rsplit('.html', 1)[0] + "/")])
      return ''

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
    menuText += '<li><a href="#global">Global Ranks for %s</a></li>' % escape(name)
    for type in types:
      menuText += '<li><a href="#%s">%s Server</a></li>\n' % (type, type.title())
    menuText += '</ul>'

    print >>out, header("%s - Player Profile - DDraceNetwork" % escape(name), menuText, "")

    print >>out, '<div id="global" class="block div-ranks">'

    hiddenFields = '<input type="hidden" name="player" value="%s">' % escape(name)

    print >>out, '<div id="remote" class="right"><form id="playerform" action="/compare/" method="get">%s<input name="player" class="typeahead" type="text" placeholder="Compare"><input type="submit" value="Compare" style="position: absolute; left: -9999px"></form></div>' % hiddenFields
    print >>out, '<script src="/jquery.js" type="text/javascript"></script>'
    print >>out, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
    print >>out, '<script src="/playersearch.js" type="text/javascript"></script>'
    print >>out, '<div class="block7"><h2>Global Ranks for %s</h2></div><br/>' % escape(name)
    print >>out, globalRanks(name, player)
    print >>out, lastFinishes(name)
    print >>out, '<br/>'
    print >>out, '</div>'

    for type in types:
      maps2 = maps[type]

      count = 0
      for map in maps2:
        if map in player[0]:
          count += 1

      print >>out, '<div id="%s" class="block div-ranks"><h2></h2><h2 class="inline">%s Server</h2> <h3 class="inline">(%d/%d maps finished)</h3><br/>' % (type, type.title(), count, len(maps2))

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
