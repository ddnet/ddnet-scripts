# -*- coding: utf-8 -*-

import sys
import re
import os
import gc
import os.path
from cgi import escape
from datetime import date, datetime
from collections import namedtuple, defaultdict
import time
import msgpack
from urllib import quote_plus
from operator import itemgetter
from collections import OrderedDict
from string import capwords
from socket import gethostbyaddr

from mysql import *
from teeworlds import *
from countryflags import *

reload(sys)
sys.setdefaultencoding('utf8')

webDir = "/var/www"

pointsDict = {
  'Novice':    (1, 0),
  'Moderate':  (2, 5),
  'Brutal':    (3,15),
  'Insane':    (4,30),
  'Dummy':     (5, 5),
  'DDmaX':     (4, 0),
  'Oldschool': (6, 0),
  'Solo':      (4, 0),
  'Race':      (2, 0)
}

def lookupIp(ip):
  try:
    return gethostbyaddr(ip)[0]
  except:
    return ip

def points(rank):
  if rank < 0 or rank > 10:
    return 0

  return {
    1 : 25,
    2 : 18,
    3 : 15,
    4 : 12,
    5 : 10,
    6 : 8,
    7 : 6,
    8 : 4,
    9 : 2,
    10 : 1
  }[rank]

def titleSubtype(type):
  if type == 'DDRACEMAX.EASY MAPS':
    return 'DDracemaX.easy Maps'
  elif type == 'DDRACEMAX.NEXT MAPS':
    return 'DDracemaX.next Maps'
  elif type == 'DDRACEMAX.PRO MAPS':
    return 'DDracemaX.pro Maps'
  else:
    return capwords(type)

def description(tile):
  return {
    'DFREEZE' : 'Deep Freeze',
    'EHOOK_START': 'Endless Hook',
    'HIT_START': 'No Hit',
    'SOLO_START': 'Solo',
    'NPC_START': 'No Player Collision',
    'SUPER_START': 'Super Jumps',
    'JETPACK_START': 'Jetpack',
    'WALLJUMP': 'WallJump',
    'NPH_START': 'No Player Hook',
    'WEAPON_SHOTGUN': 'Shotgun',
    'WEAPON_GRENADE': 'Grenade',
    'POWERUP_NINJA': 'Ninja',
    'WEAPON_RIFLE': 'Rifle',
    'JUMP': 'Customized Jumps',
    'SWITCHTIMEDOPEN': 'Timed Switch',
    'SWITCHOPEN': 'Switch',
    'TELEINEVIL': 'Evil Teleport',
    'TELEIN': 'Teleport',
    'TELECHECKIN': 'Checkpointed Teleport',
    'TELEINWEAPON': 'Weapon Teleport',
    'TELEINHOOK': 'Hook Teleport'
  }[tile]

def order(tile):
  return [
    'SOLO_START',

    'WEAPON_SHOTGUN',
    'WEAPON_GRENADE',
    'WEAPON_RIFLE',
    'POWERUP_NINJA',

    'DFREEZE',
    'EHOOK_START',
    'HIT_START',

    'NPC_START',
    'NPH_START',
    'SUPER_START',
    'JETPACK_START',
    'WALLJUMP',
    'JUMP',

    'SWITCHTIMEDOPEN',
    'SWITCHOPEN',

    'TELEIN',
    'TELEINEVIL',
    'TELECHECKIN',
    'TELEINWEAPON',
    'TELEINHOOK'
  ].index(tile)

def normalizeMapname(name):
  return re.sub('\W', '_', name)

def escapeOption(str):
  return str.replace('"', '\\"')

def textJoinNames(names):
  result = ', '.join(names[:-1])
  if names[-1]:
    result += ' & ' + names[-1]
  return result

def joinNames(names):
  result = ', '.join(names[:-1])
  if names[-1]:
    result += ' &amp; ' + names[-1]
  return result

def renderStars(points):
  return u'★' * points + u'✰' * max(5 - points, 0)

def globalPoints(type, stars):
  mo = pointsDict.get(type, (1,0))
  mult = mo[0]
  offset = mo[1]
  return stars * mult + offset

def countClients(server):
  result = 0
  for player in server.playerlist:
    if player.name != "(connecting)".decode('utf8') or player.clan != "".decode('utf8') or player.score != 0 or player.country != -1:
      result += 1
  return result

#PlayerMap = namedtuple('PlayerMap', ['teamRank', 'rank', 'points', 'nrFinishes', 'firstFinish', 'time'])
PlayerMap = namedtuple('PlayerMap', ['teamRank', 'rank', 'nrFinishes', 'firstFinish', 'time'])
Player = namedtuple('Player', ['maps', 'servers'])
Map = namedtuple('Map', ['name', 'points', 'finishes'])

def slugify2(name):
  x = '[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+'
  string = ""
  for c in name:
    if c in x or ord(c) >= 128:
      string += "-%s-" % ord(c)
    else:
      string += c
  return string

def deslugify2(string):
  try:
    n = u''
    t = 0
    i = 0

    for c in string:
      if t == 0:
        if c == '-':
          t = 1
        else:
          n += c
      else:
        if c == '-':
          n += unichr(i)
          t = 0
          i = 0
        else:
          i = i * 10 + int(c)
    return n.encode('utf-8')
  except:
    return string

def playerWebsite(name):
  return "/players/%s/" % slugify2(u'%s' % name)

def mapperWebsite(name):
  return "/mappers/%s/" % slugify2(u'%s' % name)

def splitMappers(mapperName):
  names = mapperName.split(", ")
  if len(names):
    names = names[:-1] + names[-1].split(" & ")
  return names

def makeAndString(names, ampersand = "&"):
  if len(names) < 1:
    return ""

  if len(names) == 1:
    return names[0]

  result = ""
  for name in names[:-1]:
    if result:
      result += ", "
    result += name
  result += " " + ampersand + " " + names[-1]
  return result

def formatRank(rank):
  if rank == 0:
    return ''
  return '%d.' % rank

def formatDate(date):
  return date.strftime('%Y-%m-%d %H:%M')

def formatDateExact(date):
  return date.strftime('%Y-%m-%d %H:%M:%S')

def formatDateShort(date):
  return date.strftime('%H:%M')

def formatTime(totalSeconds):
  return '%02d:%02d' % divmod(totalSeconds, 60)

def formatTimeExact(totalSeconds):
  return '%02d:%05.02f' % divmod(totalSeconds, 60)

def formatScore(score, pure = False):
  if pure:
    return str(score)
  if score == -9999:
    return ""
  return formatTime(abs(score))

def header(title, menu, header, refresh = False, stupidIncludes = False, otherIncludes = ""):
  if refresh:
    mbRefresh = '<meta http-equiv="refresh" content="120" />'
  else:
    mbRefresh = ''

  if stupidIncludes:
    mbIncludes = """    <link rel="stylesheet" href="css/bootstrap.css">
    <link rel="stylesheet" href="css/bootstrap-theme.css">
    <link rel="stylesheet" type="text/css" href="css/light.css" />"""
  else:
    mbIncludes = ''

  return """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
    <link rel="apple-touch-icon" sizes="57x57" href="/apple-touch-icon-57x57.png">
    <link rel="apple-touch-icon" sizes="114x114" href="/apple-touch-icon-114x114.png">
    <link rel="apple-touch-icon" sizes="72x72" href="/apple-touch-icon-72x72.png">
    <link rel="apple-touch-icon" sizes="144x144" href="/apple-touch-icon-144x144.png">
    <link rel="apple-touch-icon" sizes="60x60" href="/apple-touch-icon-60x60.png">
    <link rel="apple-touch-icon" sizes="120x120" href="/apple-touch-icon-120x120.png">
    <link rel="apple-touch-icon" sizes="76x76" href="/apple-touch-icon-76x76.png">
    <link rel="apple-touch-icon" sizes="152x152" href="/apple-touch-icon-152x152.png">
    <link rel="icon" type="image/png" href="/favicon-196x196.png" sizes="196x196">
    <link rel="icon" type="image/png" href="/favicon-160x160.png" sizes="160x160">
    <link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96">
    <link rel="icon" type="image/png" href="/favicon-16x16.png" sizes="16x16">
    <link rel="icon" type="image/png" href="/favicon-32x32.png" sizes="32x32">
    <meta name="msapplication-TileColor" content="#2d89ef">
    <meta name="msapplication-TileImage" content="/mstile-144x144.png">
    <meta name="viewport" content="width=device-width">
    <meta http-equiv="cache-control" content="max-age=0" />
    <meta http-equiv="cache-control" content="no-cache" />
    <meta http-equiv="expires" content="0" />
    <meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />
    <meta http-equiv="pragma" content="no-cache" />
    %s
    %s
    %s
    <link rel="stylesheet" type="text/css" href="/css.css?version=11" />
    <script src="/js.js" type="text/javascript"></script>
    <title>%s</title>
  </head>
  <body>
    <article>
    <header>
      <div class="fade">
      <menu class="contentleft">
      <div class="title"><h1><a href="/"><img class="logobig" alt="DDraceNetwork" src="/ddnet2.svg"/><img class="logosmall" alt="DDraceNetwork" src="/ddnet.svg"/></a></h1></div>
      <ul class="big">
        <li><a href="/status/">Status</a></li>
        <li><a href="/ranks/">Ranks</a></li>
        <li><a href="/releases/">Releases</a></li>
        <li><a href="/discord">Discord</a> / <a href="//forum.ddnet.tw/">Forum</a></li>
        <li><a href="/downloads/">Downloads</a></li>
        <li><a href="/tournament/">Tournaments</a></li>
        <li><a href="/skins/">Skin Database</a></li>
        <li><a href="/stats/">Statistics</a></li>
      </ul>
      %s
      </menu>
      </div>
    </header>
    <section>
    %s""" % (mbRefresh, mbIncludes, otherIncludes, title, menu, header)

def printExactSoloRecords(recordName, className, topFinishes):
  string = u'<div class="block2 %s"><h4>%s:</h4>\n' % (className, recordName)
  if len(topFinishes) > 0:
    string += '<table class="tight">\n'
    for f in topFinishes:
      if f[4] > 1:
        mbS = "es"
      else:
        mbS = ""
      string += u'  <tr title="%s, %s, %d finish%s total"><td class="rank">%d.</td><td class="time">%s</td><td><a href="%s">%s</a></td></tr>\n' % (escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[4], mbS, f[0], escape(formatTimeExact(f[2])), escape(playerWebsite(u'%s' % f[1])), escape(f[1]))
    string += '</table>\n'
  string += '</div>\n'

  return string

def printSoloRecords(recordName, className, topFinishes):
  string = u'<div class="block2 %s"><h4>%s:</h4>\n' % (className, recordName)
  if len(topFinishes) > 0:
    string += '<table class="tight">\n'
    for f in topFinishes:
      if f[4] > 1:
        mbS = "es"
      else:
        mbS = ""
      string += u'  <tr title="%s, %s, %d finish%s total"><td class="rank">%d.</td><td class="time">%s</td><td><a href="%s">%s</a></td></tr>\n' % (escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[4], mbS, f[0], escape(formatTime(f[2])), escape(playerWebsite(u'%s' % f[1])), escape(f[1]))
    string += '</table>\n'
  string += '</div>\n'

  return string

def printTeamRecords(recordName, className, topFinishes):
  string = u'<div class="block2 %s"><h4>%s:</h4>\n' % (className, recordName)
  if len(topFinishes) > 0:
    string += '<table class="tight">\n'
    for f in topFinishes:
      string += u'  <tr title="%s, %s"><td class="rank">%d.</td><td class="time">%s</td><td>%s</td></tr>\n' % (escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[0], escape(formatTime(f[2])), f[1])
    string += '</table>\n'
  string += '</div>\n'

  return string

def printLadder(name, ranks, players, number = 10):
  string = '<div class="block2 ladder"><h3>%s</h3>\n' % name
  currentRank = 0
  skips = 1
  lastPoints = 0
  lastServer = ''
  if len(ranks) > 0:
    string += '<table class="tight">\n'
    for currentPos, r in enumerate(ranks):
      if currentPos > 499:
        break
      if r[1] != lastPoints:
        lastPoints = r[1]
        currentRank += skips
        skips = 1
      else:
        skips += 1
      if currentPos > number - 1:
        string += '<tr class="allPoints" style="display: none">\n'
      else:
        string += '<tr>\n'

      #try:
      #  player = players.get(r[0])
      #  favServer = max(player[1].iteritems(), key=itemgetter(1))[0]
      #  if favServer == None:
      #    favServer = 'UNK'
      #except:
      #  favServer = 'UNK'

      #if lastServer != favServer:
      #  string += u'  <td class="rankglobal">%d.</td><td class="points">%d pts</td><td class=\"flag\"><img src=\"/countryflags/%s.png\" alt=\"%s\" height=\"15\"/></td><td><a href="%s">%s</a></td></tr>' % (currentRank, r[1], favServer, favServer, escape(playerWebsite(u'%s' % r[0])), escape(r[0]))
      #  lastServer = favServer
      #else:
      #  string += u'  <td class="rankglobal">%d.</td><td class="points">%d pts</td><td class=\"flag\">⋮</td><td><a href="%s">%s</a></td></tr>' % (currentRank, r[1], escape(playerWebsite(u'%s' % r[0])), escape(r[0]))
      string += u'  <td class="rankglobal">%d.</td><td class="points">%d pts</td><td><a href="%s">%s</a></td></tr>' % (currentRank, r[1], escape(playerWebsite(u'%s' % r[0])), escape(r[0]))
    string += '</table>\n'
  string += '</div>\n'

  return string

def isKnownPlayer(name, con, cur):
  if name in ("(connecting)", "nameless tee"):
      return True
  cur.execute("select count(distinct Name) from record_race where Name = '%s';" % (con.escape_string(name)))
  return int(cur.fetchall()[0][0]) > 0

def printPlayers(server, filt, con, cur):
  count = 0
  for player in server.playerlist:
    if filt(player):
      count += 1
  if count == 0:
    return

  print('<table class="status">')
  for player in sorted(server.playerlist, key=lambda p: (-p.score, p.name.lower())):
    if filt(player):
      print("<tr>")
      if isKnownPlayer(player.name, con, cur):
        htmlName = '<a href=\"%s\">%s</a>' % (escape(playerWebsite(u'%s' % player.name)), escape(player.name))
      else:
        htmlName = escape(player.name)

      print((u"  <td class=\"time\">%s</td><td class=\"name\">%s</td><td class=\"clan\">%s</td><td class=\"flag\"><img src=\"countryflags/%s.png\" alt=\"%s\" height=\"20\"/></td>" % (formatScore(player.score, "race" not in server.gametype.lower()), htmlName, escape(player.clan), countryFlags.get(player.country, 'default'), countryFlags.get(player.country, 'NONE'))).encode('utf-8'))
      print("</tr>")
  print("</table>")

def serverStatus(title):
  return """    <div id="global" class="block">
      <h2>%s</h2>
      <table class="table table-striped table-condensed">
        <thead>
        <tr>
          <th id="status4" style="text-align: center;">Net</th>
          <th id="status6" style="text-align: center;">IPv6</th>
          <th id="name">Name</th>
          <th id="type">Domain</th>
          <th id="host">Host</th>
          <th id="location">Location</th>
          <th id="uptime">Uptime</th>
          <th id="load">Load</th>
          <th id="network">Net ↓|↑</th>
          <th id="cpu">CPU</th>
          <th id="memory">RAM</th>
          <th id="hdd">HDD</th>
        </tr>
        </thead>
        <tbody id="servers">
        <!-- Servers here -->
        </tbody>
      </table>
      <br />
      <h3 class="ip">
        <a href="/stats/server/">Statistics</a>, <a href="https://github.com/BotoX/ServerStatus">ServerStatus</a>
      </h3>
    </div>
    <script src="js/jquery-1.10.2.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/serverstatus.js"></script>
    """ % title

childrenCount = 0
second = False
def getTSStatus():
  import ts3
  global childrenCount
  svr = ts3.TS3Server("ts.ddnet.tw", 10011, 1)
  response = svr.send_command('use port=9987')

  response = svr.send_command('serverinfo')
  if response.response['msg'] != 'ok':
    exit
  svr_info = response.data[0]

  response = svr.send_command('channellist')
  if response.response['msg'] != 'ok':
    exit
  channel_list = response.data

  response = svr.send_command('clientlist')
  if response.response['msg'] != 'ok':
    exit
  client_list = response.data

  # Start building the channel / client tree.
  # We save tree nodes in a dictionary, keyed by their id so we can find
  # them later in order to support arbitrary channel hierarchies.
  channels = {}

  # Build the root, or channel 0
  channels[0] = {
      'title': svr_info['virtualserver_name'],
      'isFolder': True,
      'expand': True,
      'children': []
  }

  # Add the channels to our tree

  for channel in channel_list:
    node = {
      'title': channel['channel_name'],
      'isFolder': True,
      'expand': True,
      'children': []
    }
    parent = channels[int(channel['pid'])]
    parent['children'].append(node)
    channels[int(channel['cid'])] = node

    if node['title'] == 'DDraceNetwork':
      ddnetChan = node

  # Add the clients to the tree

  for client in client_list:
    if client['client_type'] == '0':
      node = {
        'title': client['client_nickname'],
        'isFolder': False
      }
      channel = channels[int(client['cid'])]
      channel['children'].append(node)

  tree = [channels[0]]

  childrenCount = 0
  def renderChannel(chan, name):
    global childrenCount, second
    thisCount = 0
    result = '<div class="block3">\n<h3>%s</h3>\n<table>\n' % name
    childrenCount
    for child in chan['children']:
      if not child['isFolder']:
        result += '<tr>\n  <td>%s</td>\n</tr>\n' % child['title']
        childrenCount += 1
        thisCount += 1
    result += '</table>\n</div>\n'
    if second:
      result += '<br/>'
    if thisCount > 0:
      second = not second
      return result
    else:
      return ''

  text = ''

  text += renderChannel(ddnetChan, 'DDraceNetwork Main')
  for chan in ddnetChan['children']:
    if chan['isFolder']:
      text += renderChannel(chan, 'DDraceNetwork %s' % chan['title'])

  #if childrenCount == 0:
  #  result = '<div class="block empty" style="display:none">\n'
  #else:
  result = '<div class="block">\n'
  result += '<h3 class="ip">ts.ddnet.tw</h3>'
  mbS = ''
  if childrenCount != 1:
    mbS = 's'
  result += '<h2>DDNet Teamspeak Status: %d user%s</h2>\n' % (childrenCount, mbS)
  result += text
  result += '<br/></div>'
  return result

def address(s):
  spl = s.split(':')
  return (spl[0], int(spl[1]))

def printStatus(name, servers, doc, external = False):
  con = mysqlConnect()
  with con:
    cur = con.cursor()
    cur.execute("set names 'utf8mb4';")
    now = datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M")
    serverPlayers = OrderedDict()
    modPlayers = OrderedDict()

    serverPositions = {}

    for i in servers:
      serverPlayers[i] = 0
      serverPositions[i] = 0

    tw = []
    for i in range(4):
      tw.append(Teeworlds(timeout=20))

    for countryEntry in doc:
      country = countryEntry['name']
      for typ, svs in countryEntry['servers'].iteritems():
        modPlayers[typ] = 0
        for s in svs:
          serverAddress = address(s)
          for i, t in enumerate(tw):
            if i < 2:
              server = Server64(t, serverAddress)
            else:
              server = Server(t, serverAddress)
            server.request()
            t.serverlist.add(server)

    for t in tw: t.run_loop()

    totalPlayers = 0
    lastServer = ''

    i = 0
    for countryEntry in doc:
      country = countryEntry['name']
      for typ, svs in countryEntry['servers'].iteritems():
        for s in svs:
          for t in tw:
            server = t.serverlist.servers[i]

            if server.clients < 0:
              continue

            clients = countClients(server)

            if country != lastServer:
              lastServer = country
              serverPositions[lastServer] = i
            totalPlayers += clients
            if serverPlayers.has_key(country):
              serverPlayers[country] += clients
            if modPlayers.has_key(typ):
              modPlayers[typ] += clients
            break
          i += 1

    menuText = ""
    if len(servers) > 1:
      menuText += '<ul>'
      for i in servers:
        menuText += '<li><a href="#server-%d">%s&nbsp;[%d]</a></li> ' % (serverPositions[i], servers[i][1].replace(" ","&nbsp;"), serverPlayers[i])
      menuText += "</ul>"

    if name == "DDraceNetwork":
      print header("[%d] %s Status" % (totalPlayers, name), menuText, serverStatus("%s Status: %d players" % (name, totalPlayers)), True, True)
    else:
      print header("[%d] %s Status" % (totalPlayers, name), menuText, '<div id="global" class="block"><h2>%s Status: %d players</h2></div>' % (name, totalPlayers), True)

    print '<p class="toggle"><a title="Click to toggle whether empty servers are shown" href="#" onclick="showClass(\'empty\'); return false;">Show empty servers</a></p>'

    if name == "DDraceNetwork":
      try:
        print getTSStatus()
      except:
        pass

    inp = None

    #for i, s in enumerate(tw.serverlist):
    i = 0
    for countryEntry in doc:
      country = countryEntry['name']
      for typ, svs in countryEntry['servers'].iteritems():
        for s in svs:
          for t in tw:
            try:
              server = t.serverlist.servers[i]
              mbEmpty = ""
              clients = countClients(server)
              if clients < 1:
                mbEmpty = " empty\" style=\"display:none"

              max_clients = server.max_clients
              name = server.name

              tmp = name.strip().split(" - ")
              serverType = tmp[-1].split(" ")[0]
              serverRest = " ".join(tmp[-1].split(" ")[1:])
              if serverRest != "":
                serverRest = " %s" % serverRest

              if external or "Test" in name:
                serverName = escape(name)
                mapName = escape(server.map)
              elif not "DDrace" in name or "BLOCKER" in name or "Tournament" in name or "ADMIN" in name:
                serverName = escape(name)
                mapName = '<a href="/maps/?map=%s">%s</a>' % (quote_plus(server.map), escape(server.map))
              else:
                serverName = '%s - <a href="/ranks/%s/">%s</a>%s' % (escape(" - ".join(tmp[:-1])), escape(serverType.lower()), escape(serverType), escape(serverRest))
                mapName = '<a href="/ranks/%s/#map-%s">%s</a>' % (escape(serverType.lower()), escape (normalizeMapname(server.map)), escape(server.map))


              print((u'<div id="server-%d"><div class="block%s"><h3 class="ip">%s:%s</h3><h2>%s: %s [%d/%d]</h2><br/>' % (i, mbEmpty, lookupIp(s.split(":")[0]), s.split(":")[1], serverName, mapName, clients, max_clients)).encode('utf-8'))

              print('<div class="block3 status-players"><h3>Players</h3>')
              printPlayers(server, lambda p: p.playing, con, cur)

              print('</div><div class="block3 status-players"><h3>Spectators</h3>')
              printPlayers(server, lambda p: not p.playing, con, cur)
              print('</div><br/></div></div>')
            except:
              continue
            break
          i += 1
    print '<p class="toggle">Refreshed: %s</p>' % time.strftime("%Y-%m-%d %H:%M")
    print """</section>
    </article>
    </body>
    </html>"""

    with open('%s/status/csv/bycountry' % webDir, 'a') as f:
      f.write(date)
      for country in serverPlayers:
        f.write(",%s:%d" % (country, serverPlayers[country]))
      f.write('\n')

    with open('%s/status/csv/bymod' % webDir, 'a') as f:
      f.write(date)
      for typ in modPlayers:
        f.write(",%s:%d" % (typ, modPlayers[typ]))
      f.write('\n')
