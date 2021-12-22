# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re
import os
import gc
import os.path
from cgi import escape
from datetime import date, datetime, timedelta
from collections import namedtuple, defaultdict
from pytz import timezone
import time
import msgpack
from operator import itemgetter
from collections import OrderedDict
from string import capwords
from socket import gethostbyaddr
import json
import subprocess

from mysql import *
from teeworlds import *
from countryflags import *

try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

if sys.version_info.major < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')

webDir = "/var/www"
htmlRanksPath = "/home/teeworlds/servers/scripts/discord-ranks.html"
countries = ["NLD", "FRA", "GER", "POL", "RUS", "TUR", "IRN", "CHL", "BRA", "ARG", "USA", "CAN", "CHN", "KOR", "JAP", "SGP", "ZAF", "IND", "AUS", "OLD"]
all_tiles = [
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
]

pointsDict = {
  'Novice':    (1, 0),
  'Moderate':  (2, 5),
  'Brutal':    (3,15),
  'Insane':    (4,30),
  'Dummy':     (5, 5),
  'DDmaX':     (4, 0),
  'Oldschool': (6, 0),
  'Solo':      (4, 0),
  'Race':      (2, 0),
  'Fun':       (0, 0),
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
  return all_tiles.index(tile)

def tileHtml(tile):
  return '<span title="%s"><a href="/tiles/%s/"><img alt="%s" src="/tiles/%s.png" width="32" height="32"/></a></span> ' % (description(tile), tile, description(tile), tile)

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

def countClients7(server):
  result = 0
  for player in server["players"]:
    if player["name"] != "(connecting)".decode('utf8') or player["clan"] != "".decode('utf8') or player["score"] != 0 or player["country"] != -1:
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
    n = string
    for special_char in re.findall('(-([\d]+)-)', n):
      n = n.replace(special_char[0], unichr(int(special_char[1])))
    return n.encode('utf-8')
  except:
    return string

def playerWebsite(name):
  return "/players/%s/" % slugify2(u'%s' % name)

def mapperWebsite(name):
  return "/mappers/%s/" % slugify2(u'%s' % name)

def mapWebsite(name, country=None):
  return "/maps/%s/%s" % (escape(country.lower()), slugify2(u'%s' % name)) if country else "/maps/%s/" % slugify2(u'%s' % name)

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

def parseDatetime(str):
    return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")

def formatDate(date):
  return date.strftime('%Y-%m-%d %H:%M')

def formatDateExact(date):
  return date.strftime('%Y-%m-%d %H:%M:%S')

def formatDateShort(date):
  return date.strftime('%H:%M')

def formatDateFeedStr(str):
  return timezone("Europe/Berlin").localize(datetime.strptime(str, "%Y-%m-%d %H:%M")).isoformat("T")

def formatTimeMin(totalSeconds):
  return '%02d:%02d' % divmod(totalSeconds, 60)

def formatTime(totalSeconds):
  if totalSeconds > 3600:
    return '%02d:%02d:%02d' % (totalSeconds//3600, (totalSeconds%3600)//60, totalSeconds%60)
  else:
    return '%02d:%02d' % divmod(totalSeconds, 60)

def formatTimeExact(totalSeconds):
  if totalSeconds > 3600:
    return '%02d:%02d:%05.02f' % (totalSeconds//3600, (totalSeconds%3600)//60, totalSeconds%60)
  else:
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
    <link rel="stylesheet" type="text/css" href="/css.css?version=19" />
    <link rel="stylesheet" type="text/css" href="/css-halloween.css?version=6" />
    <script type="text/javascript" src="/js.js"></script>
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
        <li><a href="/releases/">Map Releases</a></li>
        <li><a href="/discord">Discord</a> / <a href="//forum.ddnet.tw/">Forum</a></li>
        <li><a href="//wiki.ddnet.tw/">Wiki</a></li>
        <li><a href="/downloads/">Downloads</a></li>
        <li><a href="/tournament/">Tournaments</a></li>
        <li><a href="/skins/">Skin Database</a></li>
        <li><a href="/stats/">Statistics</a></li>
        <li><a href="/staff/">Staff &amp; Contact</a></li>
        <li><a href="/switch-theme/">Switch Theme</a></li>
      </ul>
      %s
      </menu>
      </div>
    </header>
    <section>
    %s""" % (mbRefresh, mbIncludes, otherIncludes, title, menu, header)

def printExactSoloRecords(recordName, className, topFinishes, showServer = False):
  string = u'<div class="block2 %s"><h4>%s:</h4>\n' % (className, recordName)
  if len(topFinishes) > 0:
    string += '<table class="tight">\n'
    for f in topFinishes:
      if f[4] > 1:
        mbS = "es"
      else:
        mbS = ""
      mbServer = '<td class="flag"><img src="/countryflags/%s.png" alt="%s" height="15"/></td>' % (f[5], f[5]) if showServer else ''
      string += u'  <tr title="%s, %s, %d finish%s total"><td class="rank">%d.</td><td class="time">%s</td>%s<td><a href="%s">%s</a></td></tr>\n' % (escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[4], mbS, f[0], escape(formatTimeExact(f[2])), mbServer, escape(playerWebsite(u'%s' % f[1])), escape(f[1]))
    string += '</table>\n'
  string += '</div>\n'

  return string

def printSoloRecords(recordName, className, topFinishes, showServer = False):
  string = u'<div class="block2 %s"><h4>%s:</h4>\n' % (className, recordName)
  if len(topFinishes) > 0:
    string += '<table class="tight">\n'
    for f in topFinishes:
      if f[4] > 1:
        mbS = "es"
      else:
        mbS = ""
      mbServer = '<td class="flag"><img src="/countryflags/%s.png" alt="%s" height="15"/></td>' % (f[5], f[5]) if showServer else ''
      string += u'  <tr title="%s, %s, %d finish%s total"><td class="rank">%d.</td><td class="time">%s</td>%s<td><a href="%s">%s</a></td></tr>\n' % (escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[4], mbS, f[0], escape(formatTime(f[2])), mbServer, escape(playerWebsite(u'%s' % f[1])), escape(f[1]))
    string += '</table>\n'
  string += '</div>\n'

  return string

def printTeamRecords(recordName, className, topFinishes, showServer = False):
  string = u'<div class="block2 %s"><h4>%s:</h4>\n' % (className, recordName)
  if len(topFinishes) > 0:
    string += '<table class="tight">\n'
    for f in topFinishes:
      mbServer = '<td class="flag"><img src="/countryflags/%s.png" alt="%s" height="15"/></td>' % (f[4], f[4]) if showServer else ''
      string += u'  <tr title="%s, %s"><td class="rank">%d.</td><td class="time">%s</td>%s<td>%s</td></tr>\n' % (escape(formatTimeExact(f[2])), escape(formatDate(f[3])), f[0], escape(formatTime(f[2])), mbServer, f[1])
    string += '</table>\n'
  string += '</div>\n'

  return string

def printLadder(name, ranks, players, showFavServer, number = 10):
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

      if showFavServer:
        try:
          player = players.get(r[0])
          favServer = max(player[1].iteritems(), key=itemgetter(1))[0]
          if not favServer:
            favServer = 'UNK'
        except:
          favServer = 'UNK'

        string += u'  <td class="rankglobal">%d.</td><td class="points">%d pts</td><td class="flag"><img src="/countryflags/%s.png" alt="%s" height="15"/></td><td><a href="%s">%s</a></td></tr>' % (currentRank, r[1], favServer, favServer, escape(playerWebsite(u'%s' % r[0])), escape(r[0]))
      else:
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

def printPlayers7(server, filt, con, cur):
  count = 0
  for player in server["players"]:
    if filt(player):
      count += 1
  if count == 0:
    return

  print('<table class="status">')
  for player in sorted(server["players"], key=lambda p: (-p["score"], p["name"].lower())):
    if filt(player):
      print("<tr>")
      if isKnownPlayer(player["name"], con, cur):
        htmlName = '<a href=\"%s\">%s</a>' % (escape(playerWebsite(u'%s' % player["name"])), escape(player["name"]))
      else:
        htmlName = escape(player["name"])

      print((u"  <td class=\"time\">%s</td><td class=\"name\">%s</td><td class=\"clan\">%s</td><td class=\"flag\"><img src=\"countryflags/%s.png\" alt=\"%s\" height=\"20\"/></td>" % (formatScore(player["score"], "race" not in server["gametype"].lower()), htmlName, escape(player["clan"]), countryFlags.get(player["country"], 'default'), countryFlags.get(player["country"], 'NONE'))).encode('utf-8'))
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

def getDiscordStatus():
  return """<div class="block">
<h3 class="ip"><a href="https://ddnet.tw/discord">ddnet.tw/discord</a></h3><h2>DDNet Discord</h2>
<a href="https://ddnet.tw/discord"><img alt="Discord" src="discord.png"></a>
</div>"""

#  import urllib2, json
#  j = json.load(urllib2.urlopen(urllib2.Request(
#    'https://discordapp.com/api/guilds/252358080522747904/embed.json',
#    headers={'User-Agent': 'Mozilla/5.0'})))
#  num_online = 0
#  num_total = 0
#
#  for member in j["members"]:
#    if member["status"] == "online":
#      num_online += 1
#    num_total += 1
#
#  return """<div class="block">
#<h3 class="ip"><a href="https://ddnet.tw/discord">ddnet.tw/discord</a></h3><h2>DDNet Discord</h2>
#<p>Online: {}</p>
#<p>Total Members: {}</p>
#</div>""".format(num_online, num_total)

def getDiscordRanks():
  result = '<div class="block">\n'
  result += '<p class="toggle" style="float: right;"><a href="#" onclick="showClass(\'allRecords\'); return false;">Last Week / Today</a></p>\n'
  result += '<h2>Recent Top Records <a href="records/feed/"><img width="24" src="/feed.svg"/></a></h2>\n'
  with open(htmlRanksPath, 'r+') as f:
    endTime = datetime.now() - timedelta(days=1)
    for line in reversed(f.readlines()):
      [timeStr, content, title] = line.strip().split('\x1e', 2)
      allRecordsStyle = 'class="allRecords" style="display:none"'
      dt = parseDatetime(timeStr)
      attrs = ""
      if dt <= endTime:
        attrs = allRecordsStyle
      result += '<p %s><span %s>%s</span> %s %s</p>\n' % (attrs, allRecordsStyle, dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M'), content)
  result += '</div>'
  return result

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
    #if second:
    #  result += '<br/>'
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
  result += '<h3 class="ip"><a href="ts3server://ts.ddnet.tw">ts.ddnet.tw</a></h3>'
  mbS = ''
  if childrenCount != 1:
    mbS = 's'
  result += '<h2>DDNet Teamspeak</h2>\n'
  result += text
  result += '<br/></div>'
  return result

def address(s):
  spl = s.split(':')
  return (spl[0], int(spl[1]))

def serverToDict(server, con, cur, host, mapUrl):
  ip, port = address(server.address)

  players = []
  for p in server.playerlist:
    p_out = {
      'name': p.name,
      'clan': p.clan,
      'country': p.country,
      'score': p.score,
      'playing': p.playing,
    }

    if isKnownPlayer(p.name, con, cur):
      p_out['url'] = escape(playerWebsite(u'%s' % p.name))

    players.append(p_out)

  out = {
    'ip': ip,
    'port': port,
    'host': host,
    'name': server.name,
    'map': server.map,
    'gametype': server.gametype,
    'password': server.password,
    'num_players': server.players,
    'max_players': server.max_players,
    'num_clients': server.clients,
    'max_clients': server.max_clients,
    'players': players,
    'timestamp': server.request_time,
  }

  if mapUrl is not None:
    out['map_url'] = mapUrl

  return out

def server7ToDict(server, con, cur, host, mapUrl):
  ip = server["address"][0]
  port = server["address"][1]

  players = []
  for p in server["players"]:
    p_out = {
      'name': p['name'],
      'clan': p['clan'],
      'country': p['country'],
      'score': p['score'],
      'playing': p['player'] == 0,
    }

    if isKnownPlayer(p['name'], con, cur):
      p_out['url'] = escape(playerWebsite(u'%s' % p['name']))

    players.append(p_out)

  out = {
    'ip': ip,
    'port': port,
    'host': host,
    'name': server['name'],
    'map': server['map'],
    'gametype': server['gametype'],
    'password': False,
    'num_players': server['num_players'],
    'max_players': server['max_players'],
    'num_clients': server['num_clients'],
    'max_clients': server['max_clients'],
    'players': players,
    'timestamp': time.time(),
  }

  if mapUrl is not None:
    out['map_url'] = mapUrl

  return out

def printStatus(name, servers, doc, external = False):
  con = mysqlConnect()
  with con:
    cur = con.cursor()
    cur.execute("set names 'utf8mb4';")
    now = datetime.now()
    date = formatDate(now)
    serverPlayers = OrderedDict()
    modPlayers = OrderedDict()
    modPlayers["DDNet7"] = 0

    serverPositions = {}

    for i in servers:
      serverPlayers[i] = 0
      serverPositions[i] = 0

    tw = []
    for i in range(5):
      tw.append(Teeworlds(timeout=20))

    for countryEntry in doc:
      country = countryEntry['name']
      for typ, svs in countryEntry['servers'].iteritems():
        modPlayers[typ] = 0
        for s in svs:
          serverAddress = address(s)
          for i, t in enumerate(tw):
            if typ in ["DDNet", "Block", "Infection"]:
              server = Server64(t, serverAddress)
            else:
              server = Server(t, serverAddress)
            server.request()
            t.serverlist.add(server)

    for t in tw: t.run_loop()

    totalPlayers = 0
    lastServer = ''

    #ddnet7result = subprocess.check_output(['/home/teeworlds/servers/scripts/ddnet7status.py'])
    #ddnet7status = json.loads(ddnet7result.splitlines()[-1], object_pairs_hook=OrderedDict, object_hook=OrderedDict)

    i = 0
    j = 0
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
              serverPositions[lastServer] = j
            totalPlayers += clients
            if serverPlayers.has_key(country):
              serverPlayers[country] += clients
            if modPlayers.has_key(typ):
              modPlayers[typ] += clients
            break
          i += 1
          j += 1

      #for server in ddnet7status[country]:
      #  clients = countClients7(server)
      #  typ = "DDNet7" # hardcoded for now

      #  if country != lastServer:
      #    lastServer = country
      #    serverPositions[lastServer] = j
      #  totalPlayers += clients
      #  if serverPlayers.has_key(country):
      #    serverPlayers[country] += clients
      #  if modPlayers.has_key(typ):
      #    modPlayers[typ] += clients

      #  j += 1

    menuText = ""
    if len(servers) > 1:
      menuText += '<ul>'
      for i in servers:
        menuText += '<li><a href="#server-%d">%s&nbsp;[%d]</a></li> ' % (serverPositions[i], servers[i][1].replace(" ","&nbsp;"), serverPlayers[i])
      menuText += "</ul>"

    includes = '<script type="text/javascript" src="/status/js/autoreload.js"></script>'

    if name == "DDraceNetwork":
      print(header("[%d] %s Status" % (totalPlayers, name), menuText, serverStatus("%s Status: %d players" % (name, totalPlayers)), False, True, otherIncludes=includes))
    else:
      print(header("[%d] %s Status" % (totalPlayers, name), menuText, '<div id="global" class="block"><h2>%s Status: %d players</h2></div>' % (name, totalPlayers), False, otherIncludes=includes))

    print('<p class="toggle"><a href="#" title="Click to enable/disable automatic page reloads", onclick="toggleReload(); return false;">Automatic reload in <span id="autoreloadtimer">120</span> seconds</a>, <a title="Click to toggle whether empty servers are shown" href="#" onclick="showClass(\'empty\'); return false;">Show empty servers</a></p>')

    if name == "DDraceNetwork":
      #try:
      #  print getDiscordStatus()
      #except:
      #  pass

      print(getDiscordRanks())

      try:
        print(getTSStatus())
      except:
        pass

    inp = None
    js = []

    #for i, s in enumerate(tw.serverlist):
    i = 0
    j = 0
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
                mapUrl = None
                mapName = escape(server.map)
              elif typ not in ("DDNet", "Block"):
                serverName = escape(name)
                mapUrl = '/mappreview/?map=%s' % quote_plus(server.map)
                mapName = '<a href="%s">%s</a>' % (mapUrl, escape(server.map))
              else:
                serverName = '%s - <a href="/ranks/%s/">%s</a>%s' % (escape(" - ".join(tmp[:-1])), escape(serverType.lower()), escape(serverType), escape(serverRest))
                mapUrl = mapWebsite(server.map)
                mapName = '<a href="%s">%s</a>' % (mapUrl, escape(server.map))


              (ip, port) = s.split(":", 1)
              host = lookupIp(ip)
              print((u'<div id="server-%d"><div class="block%s"><h3 class="ip"><a href="ddnet:%s:%s">%s:%s</a></h3><h2>%s: %s [%d/%d]</h2><br/>' % (j, mbEmpty, ip, port, host, port, serverName, mapName, clients, max_clients)).encode('utf-8'))

              print('<div class="block3 status-players"><h3>Players</h3>')
              printPlayers(server, lambda p: p.playing, con, cur)

              print('</div><div class="block3 status-players"><h3>Spectators</h3>')
              printPlayers(server, lambda p: not p.playing, con, cur)
              print('</div><br/></div></div>')

              js.append(serverToDict(server, con, cur, host, mapUrl))
            except:
              continue
            break
          i += 1
          j += 1

      #for server in ddnet7status[country]:
      #  mbEmpty = ""
      #  clients = countClients7(server)
      #  if clients < 1:
      #    mbEmpty = " empty\" style=\"display:none"

      #  max_clients = server["max_clients"]
      #  name = server["name"]

      #  tmp = name.strip().split(" - ")
      #  serverType = tmp[-1].split(" ")[0]
      #  serverRest = " ".join(tmp[-1].split(" ")[1:])
      #  if serverRest != "":
      #    serverRest = " %s" % serverRest

      #  if external or "Test" in name:
      #    serverName = escape(name)
      #    mapUrl = None
      #    mapName = escape(server["map"])
      #  elif not "DDrace" in name or "BLOCKER" in name or "Tournament" in name or "ADMIN" in name:
      #    serverName = escape(name)
      #    mapUrl = '/mappreview/?map=%s' % quote_plus(server["map"])
      #    mapName = '<a href="%s">%s</a>' % (mapUrl, escape(server["map"]))
      #  else:
      #    serverName = '%s - <a href="/ranks/%s/">%s</a>%s' % (escape(" - ".join(tmp[:-1])), escape(serverType.lower()), escape(serverType), escape(serverRest))
      #    mapUrl = mapWebsite(server["map"])
      #    mapName = '<a href="%s">%s</a>' % (mapUrl, escape(server["map"]))

      #  ip = server["address"][0]
      #  port = server["address"][1]
      #  host = lookupIp(ip)
      #  print((u'<div id="server-%d"><div class="block%s"><h3 class="ip"><a href="teeworlds:%s:%s">%s:%s</a></h3><h2>%s: %s [%d/%d]</h2><br/>' % (j, mbEmpty, ip, port, host, port, serverName, mapName, clients, max_clients)).encode('utf-8'))

      #  print('<div class="block3 status-players"><h3>Players</h3>')
      #  printPlayers7(server, lambda p: p["player"] == 0, con, cur)

      #  print('</div><div class="block3 status-players"><h3>Spectators</h3>')
      #  printPlayers7(server, lambda p: p["player"] == 1, con, cur)
      #  print('</div><br/></div></div>')

      #  js.append(server7ToDict(server, con, cur, host, mapUrl))
      #  j += 1

    print('<p class="toggle">Refreshed: %s</p>' % formatDate(time))
    print("""</section>
    </article>
    </body>
    </html>""")

    with open('%s/status/index.json' % webDir, 'w') as f:
      f.write(json.dumps(js))

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

def getRecords(cursor, startTime, endTime):
    cursor.execute("""
select Name, lll.Map, Time, min(lll.Timestamp), min(Type), Server, max(OldTime), Points, Country from
(
select Name, Map, Time, Timestamp, "2 Top 1 rank" as Type, (select Time from record_race where Map = l.map and Timestamp < "{0}" order by Time limit 1) as OldTime, Country from (select Timestamp, Name, Map, Time, Server as Country from record_race where Timestamp >= "{0}" and Timestamp < "{1}") as l where Time <= (select min(Time) from record_race where Map = l.Map)
union all
select record_teamrace.Name, record_teamrace.Map, record_teamrace.Time, record_teamrace.Timestamp, "1 Top 1 team rank" as Type, OldTime, record_race.Server as Country from (select ID, (select Time from record_teamrace where Map = l.Map and ID != l.ID and Timestamp < "{0}" order by Time limit 1) as OldTime from (select distinct ID, Map, Time from record_teamrace where Timestamp >= "{0}" and Timestamp < "{1}") as l left join (select Map, min(Time) as minTime from record_teamrace group by Map) as r on l.Map = r.Map where Time = minTime) as ll inner join record_teamrace on ll.ID = record_teamrace.ID join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time and record_teamrace.Timestamp = record_race.Timestamp
union all
select Name, Map, Time, Timestamp, "5 Worst rank on DDNet" as Type, (select Time from record_race where Timestamp < "{0}" and Map != "Time Shop" and Map != "Care for your Time" order by Time desc limit 1) as OldTime, Server as Country from (select * from record_race where Map != "Time Shop" and Map != "Care for your Time" and Time > (select Time from record_race where Timestamp < "{0}" and Map != "Time Shop" and Map != "Care for your Time" order by Time desc limit 1) order by Time desc) as llll where Timestamp >= "{0}" and Timestamp < "{1}"
) as lll join record_maps on lll.Map = record_maps.Map
where lll.Map != "Nyan Cat" and record_maps.Server != "Fun" group by Name, Map, Time order by lll.Timestamp, Name asc;
    """.format(formatDateExact(startTime), formatDateExact(endTime)))
    return cursor.fetchall()

#    cursor.execute("""
#select Name, lll.Map, Time, min(lll.Timestamp), min(Type), Server, max(OldTime), Points, Country from
#(
#select Name, Map, Time, Timestamp, "2 Top 1 rank" as Type, (select Time from record_race where Map = l.map and Timestamp < "{0}" order by Time limit 1) as OldTime, Country from (select Timestamp, Name, Map, Time, Server as Country from record_race where Timestamp >= "{0}" and Timestamp < "{1}") as l where Time <= (select min(Time) from record_race where Map = l.Map)
#union all
#select record_teamrace.Name, record_teamrace.Map, record_teamrace.Time, record_teamrace.Timestamp, "1 Top 1 team rank" as Type, OldTime, record_race.Server as Country from (select ID, (select Time from record_teamrace where Map = l.Map and ID != l.ID and Timestamp < "{0}" order by Time limit 1) as OldTime from (select distinct ID, Map, Time from record_teamrace where Timestamp >= "{0}" and Timestamp < "{1}") as l left join (select Map, min(Time) as minTime from record_teamrace group by Map) as r on l.Map = r.Map where Time = minTime) as ll inner join record_teamrace on ll.ID = record_teamrace.ID join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time and record_teamrace.Timestamp = record_race.Timestamp
#union all
#select Name, record_race.Map as Map, Time, record_race.Timestamp as Timestamp, "4 Finish" as Type, NULL as OldTime, record_race.Server as Country from record_race join record_maps on record_race.Map = record_maps.Map where record_race.Timestamp >= "{0}" and record_race.Timestamp < "{1}" and (record_maps.Points >= 30 or (record_maps.Points >= 20 and record_maps.Server = "Solo") or (record_maps.Points >= 10 and record_maps.Server = "Race"))
#union all
#select record_teamrace.Name, record_teamrace.Map as Map, record_teamrace.Time, record_teamrace.Timestamp as Timestamp, "3 Team finish" as Type, NULL as OldTime, record_race.Server as Country from record_teamrace join record_maps on record_teamrace.Map = record_maps.Map join record_race on record_teamrace.Map = record_race.Map and record_teamrace.Name = record_race.Name and record_teamrace.Time = record_race.Time and record_teamrace.Timestamp = record_race.Timestamp where record_teamrace.Timestamp >= "{0}" and record_teamrace.Timestamp < "{1}" and (record_maps.Points >= 30 or (record_maps.Points >= 20 and record_maps.Server = "Solo") or (record_maps.Points >= 10 and record_maps.Server = "Race"))
#) as lll join record_maps on lll.Map = record_maps.Map
#where lll.Map != "Nyan Cat" group by Name, Map, Time order by lll.Timestamp;
#    """.format(formatDateExact(startTime), formatDateExact(endTime)))
#    return cursor.fetchall()
