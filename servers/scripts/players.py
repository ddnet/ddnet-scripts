#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
from cgi import escape
from datetime import datetime, timedelta
import cStringIO
import msgpack
from diskcache import Cache
from operator import itemgetter
import urllib
import json
from gc import collect
from os.path import getmtime
#from guppy import hpy

reload(sys)
sys.setdefaultencoding('utf8')

data = {}
last = None

playersFile = '%s/players.msgpack' % webDir
playersCache = '/home/teeworlds/servers/players-cache'
cache = Cache(playersCache, eviction_policy='none', sqlite_auto_vacuum=0, sqlite_journal_mode='off', cull_limit=0)

con = mysqlConnect()
con.autocommit(True)

def tableHeader(name, id):
  return '<table id="%s" class="%s"><thead><tr><th class="unMapTr">Map</th><th class="unPtsTr">Pts</th><th class="unFinTr">Finishers</th></tr></thead><tbody>\n' % (id, name)

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  def reloadData():
    global data, last
    now = datetime.now()
    if not last or last < getmtime(playersFile):
      try:
        del data
        gc.collect()
      except NameError:
        pass
      with open(playersFile, 'rb') as inp:
        unpacker = msgpack.Unpacker(inp)
        data = {}
        data['types'] = unpacker.unpack()
        data['maps'] = unpacker.unpack()
        data['totalPoints'] = unpacker.unpack()
        data['pointsRanks'] = unpacker.unpack()
        data['weeklyPointsRanks'] = unpacker.unpack()
        data['monthlyPointsRanks'] = unpacker.unpack()
        data['yearlyPointsRanks'] = unpacker.unpack()
        data['teamrankRanks'] = unpacker.unpack()
        data['rankRanks'] = unpacker.unpack()
        data['serverRanks'] = unpacker.unpack()
      gc.collect()
      last = getmtime(playersFile)

  def query(sql):
    global con, cur
    try:
      cur.execute(sql)
    except:
      con = mysqlConnect()
      con.autocommit(True)
      cur = con.cursor()
      cur.execute("set names 'utf8mb4';")
      cur.execute(sql)

  def printPersonalResult(name, ranks, player):
    string = '<div class="block2 ladder"><h3>%s</h3>\n<p class="pers-result">' % name
    result = getPersonalResult(ranks, player)
    if result:
      string += '%d. with %d points' % (result[0], result[1])
    else:
      string += 'Unranked'
    string += '</p></div>'

    return string

  def getPersonalResultJson(ranks, player):
    result = getPersonalResult(ranks, player)
    if result:
      return {'rank': result[0], 'points': result[1]}
    else:
      return {'rank': 'unranked'}

  def getPersonalResult(ranks, player):
    found = False
    currentRank = 0
    skips = 1
    lastPoints = 0

    for r in ranks:
      if r[1] != lastPoints:
        lastPoints = r[1]
        currentRank += skips
        skips = 1
      else:
        skips += 1

      if r[0] == player:
        return (currentRank, r[1])
    return None

  def globalRanks(name, player):
    out = cStringIO.StringIO()

    print >>out, '<div class="block7">'
    print >>out, printPersonalResult("Points (%d total)" % data['totalPoints'], data['pointsRanks'], name)
    print >>out, printPersonalResult("Team Rank", data['teamrankRanks'], name)
    print >>out, printPersonalResult("Rank", data['rankRanks'], name)
    print >>out, '<br/>'
    print >>out, printPersonalResult("Points (last year)", data['yearlyPointsRanks'], name)
    print >>out, printPersonalResult("Points (last month)", data['monthlyPointsRanks'], name)
    print >>out, printPersonalResult("Points (last week)", data['weeklyPointsRanks'], name)
    print >>out, '<br/>'

    try:
      favServer = max(player[1].iteritems(), key=itemgetter(1))[0]
      if favServer == None or favServer == "":
        favServer = 'UNK'
    except:
      favServer = 'UNK'

    print >>out, '<div class="block2 ladder"><h3>Favorite Server</h3>\n<p class="pers-result"><img src="/countryflags/%s.png" alt="%s" height="20" /></p></div>' % (favServer, favServer)

    try:
      query("select Timestamp, Map, Time from record_race where Name = '%s' order by Timestamp limit 1;" % con.escape_string(name))
      rows = cur.fetchall()
      row = rows[0]

      for row in rows:
        type = ''
        for t in data['types']:
          for (map, points, finishes) in data['maps'][t]:
            if row[1] == map:
              type = t
              break
          if type != '':
            break
      dateWithTz = escape(formatDateTimeTz(row[0]))
      print >>out, '<div class="block2 ladder"><h3>First Finish</h3>\n<p class="personal-result"><span data-type="date" data-date="%s" data-datefmt="datetime">%s</span>: <a href="%s">%s</a> (%s)</p></div>' % (dateWithTz, escape(formatDate(row[0])), mapWebsite(row[1]), escape(row[1]), escape(formatTime(row[2])))
    except:
      pass

    print >>out, '</div>'

    return out.getvalue()

  def favoritePartners(name):
    out = cStringIO.StringIO()

    try:
      query("select r.Name, count(r.Name) from (select Name, ID from record_teamrace where Name = '%s') as l inner join (select ID, Name from record_teamrace) as r on l.ID = r.ID and l.Name != r.Name group by r.Name order by count(r.Name) desc limit 10;" % con.escape_string(name))
      rows = cur.fetchall()

      pos = 1
      lastFinishes = 0
      skips = 0

      if len(rows) > 0:
        print >>out, '<div class="block6 ladder" style="margin-left: 1em;"><h3>Favorite Partners</h3>\n<table class="tight">'

        for row in rows:
          name = row[0]
          finishes = row[1]

          if finishes != lastFinishes:
            lastFinishes = finishes
            pos += skips
            skips = 1
          else:
            skips += 1

          encodedName = slugify2(u'%s' % name.encode('utf-8'))
          print >>out, '<tr><td>%d. <a href="/players/%s/">%s</a>: %d ranks</td></tr>' % (pos, encodedName, escape(name), finishes)

        print >>out, '</table></div>'
    except:
      pass

    return out.getvalue()

  def lastFinishes(name):
    out = cStringIO.StringIO()

    print >>out, '<div class="block6 ladder"><h3>Last Finishes</h3><table class="tight">'

    query("select record_race.Timestamp, record_race.Map, Time, record_race.Server, record_maps.Server from record_race left join record_maps on record_race.Map = record_maps.Map where Name = '%s' order by record_race.Timestamp desc limit 10;" % con.escape_string(name))
    rows = cur.fetchall()

    for row in rows:
      type = ''
      for t in data['types']:
        for (map, points, finishes) in data['maps'][t]:
          if row[1] == map:
            type = t
            break
        if type != '':
          break
      dateWithTz = escape(formatDateTimeTz(row[0]))
      print >>out, '<tr><td><span data-type="date" data-date="%s" data-datefmt="datetime">%s</span>: <img src="/countryflags/%s.png" alt="%s" height="15"/> <a href="/ranks/%s/">%s</a>: <a href="%s">%s</a> (%s)</td></tr>' % (dateWithTz, escape(formatDate(row[0])), row[3], row[3], row[4].lower(), row[4], mapWebsite(row[1]), escape(row[1]), escape(formatTime(row[2])))

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
    for type in data['types']:
      menuText += '<li><a href="#%s">%s Server</a></li>\n' % (type, type)
    menuText += '</ul>'

    print >>out, header("Comparison of %s - DDraceNetwork" % andText, menuText, "")

    hiddenFields = ''
    for (name, player) in namePlayers:
      hiddenFields += '<input type="hidden" name="player" value="%s">' % escape(name)

    print >>out, '<div id="global" class="block div-ranks">'
    print >>out, '<div id="remote" class="right"><form id="playerform" action="/players/" method="get"><input id="playersearch" name="player" class="typeahead" type="text" placeholder="Player search"><input type="submit" value="Player search" style="position: absolute; left: -9999px"></form><br>'
    print >>out, '<form id="playerform2" action="/compare/" method="get">%s<input name="player" class="typeahead" type="text" placeholder="Add to comparison"><input type="submit" value="Add to comparison" style="position: absolute; left: -9999px"></form></div>' % hiddenFields
    print >>out, '<script src="/players-data/jquery-2.2.4.min.js" type="text/javascript"></script>'
    print >>out, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
    print >>out, '<script src="/playersearch.js?version=2" type="text/javascript"></script>'
    print >>out, '<script type="text/javascript" src="/players-data/jquery.tablesorter.js"></script>'
    print >>out, '<script type="text/javascript" src="/players-data/sorter.js"></script>'
    print >>out, '<script>'
    print >>out, '  var input = document.getElementById("playersearch");'
    print >>out, '  input.focus();'
    print >>out, '  input.select();'
    print >>out, '</script>'
    print >>out, '<link rel="stylesheet" type="text/css" href="/players-data/css-sorter.css">'

    for (name, player) in namePlayers:
      print >>out, '<div class="block7"><h2>Global Ranks for <a href="%s">%s</a></h2></div><br/>' % (playerWebsite(name), escape(name))
      print >>out, globalRanks(name, player)
      print >>out, '<br/>'
    print >>out, '</div>'

    for type in data['types']:
      maps2 = data['maps'][type]
      print >>out, '<div id="%s" class="block div-ranks"><h2>%s Server</h2>' % (type, type)

      for (name, player) in namePlayers:
        print >>out, '<div class="block2 ladder"><h2>%s</h2></div>' % name
        print >>out, printPersonalResult("Points (%d total)" % data['serverRanks'][type][0], data['serverRanks'][type][1], name)
        print >>out, printPersonalResult("Team Rank", data['serverRanks'][type][2], name)
        print >>out, printPersonalResult("Rank", data['serverRanks'][type][3], name)
        print >>out, '<br/>'

      unfinishedString = tableHeader("unfinTable1", "unfinTable1-" + type)

      tblString = '<div style="overflow: auto;"><table class="spacey"><thead><tr><th>Map</th><th>Points</th><th colspan="%d">Time</th><th colspan="%d">Rank</th><th colspan="%d">Team Rank</th></tr><tr><th></th><th></th>%s%s%s</tr></thead><tbody>\n' % (len(namePlayers), len(namePlayers), len(namePlayers), tableText, tableText, tableText)
      found = False
      allFinished = True

      for map, points, finishes in maps2:
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
              tmpStrings[i][0] = '<td class="rank verticalLine">%s</td>' % escape(formatTimeMin(player[0][map][4]))
              tmpStrings[i][1] = '<td class="rank verticalLine">%s</td>' % formatRank(player[0][map][1])
              tmpStrings[i][2] = '<td class="rank verticalLine">%s</td>' % formatRank(player[0][map][0])
            else:
              tmpStrings[i][0] = '<td class="rank">%s</td>' % escape(formatTimeMin(player[0][map][4]))
              tmpStrings[i][1] = '<td class="rank">%s</td>' % formatRank(player[0][map][1])
              tmpStrings[i][2] = '<td class="rank">%s</td>' % formatRank(player[0][map][0])
          i += 1

        if foundNow:
          tblString += '<tr><td><a href="%s">%s</a></td><td class="smallpoints">%d</td>' % (mapWebsite(map), escape(map), points)
          for i in range(len(namePlayers)):
            tblString += tmpStrings[i][0]
          for i in range(len(namePlayers)):
            tblString += tmpStrings[i][1]
          for i in range(len(namePlayers)):
            tblString += tmpStrings[i][2]
          tblString += '</tr>\n'
        else:
          allFinished = False
          unfinishedString += '<tr><td><a href="%s">%s</a></td><td class="rank">%d</td><td class="rank">%d</td></tr>' % (mapWebsite(map), escape(map), points, finishes)

      unfinishedString += '</tbody></table>'
      unfinishedString += tableHeader("unfinTable2", "unfinTable2-" + type) + '</tbody></table>'
      unfinishedString += tableHeader("unfinTable3", "unfinTable3-" + type) + '</tbody></table>'
      tblString += '</tbody></table></div>'
      if found:
        print >>out, tblString

      if allFinished:
        print >>out, '<p><strong>All maps on %s finished by %s!</strong></p>' % (type, orText)
      else:
        print >>out, '<input type="checkbox" id="checkbox_%s" checked="checked" /><label for="checkbox_%s"><p><a><strong>Unfinished maps (show/hide)</strong></a></p></label>' % (type, type)
        print >>out, '<div class="unfinishedmaps">'
        print >>out, unfinishedString
        print >>out, '</div>'
      print >>out, '</div>'

    print >>out, """  </section>
  </article>
  %s
  </body>
  </html>""" % printDateTimeScript()

    #h = hpy()
    #print h.heap()

    return out.getvalue()

  def application(env, start_response):
    path = env['PATH_INFO']

    if path.startswith('/compare/'):
      if len(path.split('/')) > 20:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        with open('%s/players/index.html' % webDir, 'rb') as err:
          return err.read()

      if (not path.endswith("/")) or path.endswith(".html"):
        start_response('301 Moved Permanently', [('Location', path.rstrip('/').rsplit('.html', 1)[0] + "/")])
        return ''

      reloadData()

      namePlayers = []
      for n in path.split('/')[2:-1]:
        name = deslugify2(u'%s' % n.encode('utf-8'))
        player = cache.get(name)

        if not player:
          start_response('404 Not Found', [('Content-Type', 'text/html')])
          with open('%s/players/index.html' % webDir, 'rb') as err:
            return err.read()

        namePlayers.append((name, player))

      if len(namePlayers) == 0:
        qs = env['QUERY_STRING'].split('&player=')
        if not qs[0].startswith('player='):
          start_response('404 Not Found', [('Content-Type', 'text/html')])
          with open('%s/players/index.html' % webDir, 'rb') as err:
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
        q = urllib.unquote_plus(qs[7:])

        newPath = '/players/' + slugify2(u'%s' % q).encode('utf-8') + '/'
        start_response('301 Moved Permanently', [('Location', newPath)])
        return ''

      if len(qs) > 0 and qs.startswith('query='):
        q = urllib.unquote_plus(qs[6:])
        ql = q.lower()

        jsonT = []
        reloadData()
        for r in data['pointsRanks']:
          if r[0].lower().startswith(ql):
            jsonT.append({'name': r[0], 'points': r[1]})
            if len(jsonT) > 10:
              break

        for r in data['pointsRanks']:
          if ql in r[0].lower() and {'name': r[0], 'points': r[1]} not in jsonT:
            jsonT.append({'name': r[0], 'points': r[1]})
            if len(jsonT) > 10:
              break

        start_response('200 OK', [('Content-Type', 'application/json')])
        return json.dumps(jsonT)

      if len(qs) > 0 and qs.startswith('json='):
        q = urllib.unquote_plus(qs[5:])

        start_response('200 OK', [('Content-Type', 'application/json')])

        jsonT = []
        reloadData()
        player = cache.get(q)

        if player:
          for map in player[0]:
            jsonT.append(map)

        return json.dumps(jsonT)

      if len(qs) > 0 and qs.startswith('json2='):
        q = urllib.unquote_plus(qs[6:])

        start_response('200 OK', [('Content-Type', 'application/json')])

        jsonT = OrderedDict()
        reloadData()
        player = cache.get(q)

        if player:
          name = q
          jsonT['player'] = name

          jsonT['points'] = getPersonalResultJson(data['pointsRanks'], name)
          jsonT['points']['total'] = data['totalPoints']
          jsonT['team_rank'] = getPersonalResultJson(data['teamrankRanks'], name)
          jsonT['rank'] = getPersonalResultJson(data['rankRanks'], name)
          jsonT['points_last_month'] = getPersonalResultJson(data['monthlyPointsRanks'], name)
          jsonT['points_last_week'] = getPersonalResultJson(data['weeklyPointsRanks'], name)

          query("select Timestamp, Map, Time from record_race where Name = '%s' order by Timestamp limit 1;" % con.escape_string(name))
          rows = cur.fetchall()
          row = rows[0]
          jsonT['first_finish'] = OrderedDict([('timestamp', time.mktime(row[0].timetuple())), ('map', row[1]), ('time', row[2])])

          query("select record_race.Timestamp, record_race.Map, Time, record_race.Server, record_maps.Server from record_race left join record_maps on record_race.Map = record_maps.Map where Name = '%s' order by record_race.Timestamp desc limit 10;" % con.escape_string(name))
          rows = cur.fetchall()
          jsonT['last_finishes'] = []
          for row in rows:
            jsonT['last_finishes'].append(OrderedDict([('timestamp', time.mktime(row[0].timetuple())), ('map', row[1]), ('time', row[2]), ('country', row[3]), ('type', row[4])]))

          query("select r.Name, count(r.Name) from (select Name, ID from record_teamrace where Name = '%s') as l inner join (select ID, Name from record_teamrace) as r on l.ID = r.ID and l.Name != r.Name group by r.Name order by count(r.Name) desc limit 10;" % con.escape_string(name))
          rows = cur.fetchall()
          jsonT['favoritePartners'] = []
          for row in rows:
            jsonT['favoritePartners'].append(OrderedDict([('name', row[0]), ('finishes', row[1])]))

          jsonT['types'] = OrderedDict()
          for typ in data['types']:
            jsonT['types'][typ] = OrderedDict([('points', getPersonalResultJson(data['serverRanks'][typ][1], name))])
            jsonT['types'][typ]['points']['total'] = data['serverRanks'][typ][0]
            jsonT['types'][typ]['team_rank'] = getPersonalResultJson(data['serverRanks'][typ][2], name)
            jsonT['types'][typ]['rank'] = getPersonalResultJson(data['serverRanks'][typ][3], name)

            maps2 = data['maps'][typ]
            jsonT['types'][typ]['maps'] = OrderedDict()
            for map, points, finishes in maps2:
              jsonT['types'][typ]['maps'][map] = OrderedDict([('points', points), ('total_finishes', finishes), ('finishes', 0)])
              if map in player[0]:
                timestamp = player[0][map][3]
                if isinstance(timestamp, str):
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                if player[0][map][0]:
                  jsonT['types'][typ]['maps'][map]['team_rank'] = player[0][map][0]
                jsonT['types'][typ]['maps'][map]['rank'] = player[0][map][1]
                jsonT['types'][typ]['maps'][map]['time'] = player[0][map][4]
                jsonT['types'][typ]['maps'][map]['finishes'] = player[0][map][2]
                jsonT['types'][typ]['maps'][map]['first_finish'] = time.mktime(timestamp.timetuple())

        return json.dumps(jsonT)

      start_response('200 OK', [('Content-Type', 'text/html')])
      with open('%s/players/index.html' % webDir, 'rb') as err:
        return err.read()

    if len(path.split('/')) > 4:
      start_response('404 Not Found', [('Content-Type', 'text/html')])
      with open('%s/players/index.html' % webDir, 'rb') as err:
        return err.read()

    if (not path.endswith("/")) or path.endswith(".html"):
      start_response('301 Moved Permanently', [('Location', path.rstrip('/').rsplit('.html', 1)[0] + "/")])
      return ''

    parts = path.split('/')
    rawName = u'%s' % parts[2].encode('utf-8')
    try:
      name = deslugify2(rawName)
    except:
      name = rawName
    slugName = slugify2(u'%s' % name.encode('utf-8'))
    if slugName != rawName:
      start_response('301 Moved Permanently', [('Location', "%s/%s/%s/" % (parts[0].encode('utf-8'), parts[1].encode('utf-8'), slugName.encode('utf-8')))])
      return ''

    reloadData()
    player = cache.get(name)

    if not player:
      start_response('404 Not Found', [('Content-Type', 'text/html')])
      with open('%s/players/index.html' % webDir, 'rb') as err:
        return err.read()

    start_response('200 OK', [('Content-Type', 'text/html')])

    out = cStringIO.StringIO()

    menuText = '<ul>'
    menuText += '<li><a href="#global">Global Ranks for %s</a></li>' % escape(name)
    for type in data['types']:
      menuText += '<li><a href="#%s">%s Server</a></li>\n' % (type, type)
    menuText += '</ul>'

    print >>out, header("%s - Player Profile - DDraceNetwork" % escape(name), menuText, "")

    print >>out, '<div id="global" class="block div-ranks">'

    hiddenFields = '<input type="hidden" name="player" value="%s">' % escape(name)

    print >>out, '<div id="remote" class="right"><form id="playerform" action="/players/" method="get"><input id="playersearch" name="player" class="typeahead" type="text" placeholder="Player search"><input type="submit" value="Player search" style="position: absolute; left: -9999px"></form><br>'
    print >>out, '<form id="playerform2" action="/compare/" method="get">%s<input name="player" class="typeahead" type="text" placeholder="Compare"><input type="submit" value="Compare" style="position: absolute; left: -9999px"></form></div>' % hiddenFields
    print >>out, '<script src="/jquery.js" type="text/javascript"></script>'
    print >>out, '<script src="/typeahead.bundle.js" type="text/javascript"></script>'
    print >>out, '<script src="/playersearch.js?version=2" type="text/javascript"></script>'
    print >>out, '<script type="text/javascript" src="/players-data/jquery.tablesorter.js"></script>'
    print >>out, '<script type="text/javascript" src="/players-data/sorter.js"></script>'
    print >>out, '<script>'
    print >>out, '  var input = document.getElementById("playersearch");'
    print >>out, '  input.focus();'
    print >>out, '  input.select();'
    print >>out, '</script>'
    print >>out, '<link rel="stylesheet" type="text/css" href="/players-data/css-sorter.css">'

    print >>out, '<div class="block7"><h2>Global Ranks for %s</h2></div><br/>' % escape(name)

    print >>out, globalRanks(name, player)
    print >>out, lastFinishes(name)
    print >>out, favoritePartners(name)
    print >>out, '<br/>'
    print >>out, '</div>'

    for type in data['types']:
      maps2 = data['maps'][type]

      count = 0
      for map, points, finishes in maps2:
        if map in player[0]:
          count += 1

      print >>out, '<div id="%s" class="block div-ranks"><h2></h2><h2 class="inline">%s Server</h2> <h3 class="inline">(%d/%d maps finished)</h3><br/>' % (type, type, count, len(maps2))

      print >>out, printPersonalResult("Points (%d total)" % data['serverRanks'][type][0], data['serverRanks'][type][1], name)
      print >>out, printPersonalResult("Team Rank", data['serverRanks'][type][2], name)
      print >>out, printPersonalResult("Rank", data['serverRanks'][type][3], name)
      print >>out, '<br/>'

      unfinishedString = tableHeader("unfinTable1", "unfinTable1-" + type)

      tblString = '<div style="overflow: auto;"><table class="spacey"><thead><tr><th>Map</th><th>Points</th><th>Team Rank</th><th>Rank</th><th>Time</th><th>Finishes</th><th>First Finish</th></tr></thead><tbody>\n'
      found = False
      allFinished = True

      for map, points, finishes in maps2:
        if map in player[0]:
          found = True
          timestamp = player[0][map][3]
          if isinstance(timestamp, str):
              timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
          dateWithTz = escape(formatDateTimeTz(timestamp))
          tblString += '<tr><td><a href="%s">%s</a></td><td class="smallpoints">%d</td><td class="rank">%s</td><td class="rank">%s</td><td class="rank">%s</td><td class="rank">%d</td><td class="rank"><span data-type="date" data-date="%s" data-datefmt="datetime">%s</span></td></tr>\n' % (mapWebsite(map), escape(map), points, formatRank(player[0][map][0]), formatRank(player[0][map][1]), escape(formatTimeMin(player[0][map][4])), player[0][map][2], dateWithTz, escape(formatDate(timestamp)))
        else:
          allFinished = False
          unfinishedString += '<tr><td><a href="%s">%s</a></td><td class="rank">%d</td><td class="rank">%d</td></tr>' % (mapWebsite(map), escape(map), points, finishes)

      unfinishedString += '</tbody></table>'
      unfinishedString += tableHeader("unfinTable2", "unfinTable2-" + type) + '</tbody></table>'
      unfinishedString += tableHeader("unfinTable3", "unfinTable3-" + type) + '</tbody></table>'
      tblString += '</tbody></table></div>'
      if found:
        print >>out, tblString

      if allFinished:
        print >>out, '<p><strong>All maps on %s finished!</strong></p>' % type
      else:
        print >>out, '<input type="checkbox" id="checkbox_%s" checked="checked" /><label for="checkbox_%s"><p><a><strong>Unfinished maps (show/hide)</strong></a></p></label>' % (type, type)
        print >>out, '<div class="unfinishedmaps">'
        print >>out, unfinishedString
        print >>out, '</div>'
      print >>out, '</div>'

    generatedTime = datetime.fromtimestamp(last).strftime("%Y-%m-%d %H:%M:%S")
    print >>out, """    <p class="toggle">Refreshed: <span data-type="date" data-date="%s" data-datefmt="datetime">%s</span></p>
    </section>
  </article>
  %s
  </body>
  </html>""" % (generatedTime, generatedTime, printDateTimeScript())

    #h = hpy()
    #print h.heap()

    return out.getvalue()
