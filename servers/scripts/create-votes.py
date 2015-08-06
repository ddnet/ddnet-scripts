#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ddnet import *
import sys

reload(sys)
sys.setdefaultencoding('utf8')

def truncate(s, length, encoding='utf-8'):
  encoded = s.encode(encoding)[:length]
  return encoded.decode(encoding, 'ignore')

serverStrings = {
  'Novice'   : '              Novice Server',
  'Moderate' : '           Moderate Server',
  'Brutal'   : '                Brutal Server',
  'DDmaX'    : '                DDmaX Server',
  'Oldschool': '            Oldschool Server',
  'Solo'     : '                 Solo Server',
  'Race'     : '                 Race Server'
}

server = sys.argv[1]

con = mysqlConnect()
f = open('types/%s/maps' % server.lower(), 'r')

motdSkeleton = open('motd/skeleton', 'rb').read()

localString = ""
try:
  localString = open('motd/local', 'rb').read().rstrip('\n')
except:
  pass

execString = """exec reset.cfg
exec types/%s/reset.cfg
exec types/%s/flexname.cfg
clear_votes
exec types/%s/flexvotes.cfg
exec types/%s/votes.cfg""" % (server.lower(), server.lower(), server.lower(), server.lower())

motdNews = ""
for line in open('motd/news', 'rb'):
  if len(motdNews) > 0:
    motdNews += '\\n'
  motdNews += line.rstrip('\n')

with con:
  cur = con.cursor()
  cur.execute("set names 'utf8';");

  knownTexts = set([])

  for line in f:
    words = line.rstrip('\n').split('|')
    if line[0] == '$':
      print(line.rstrip('\n')[1:])
      continue

    if len(words) == 0 or not words[0].isdigit():
      text = line.rstrip('\n')
      while len(text) == 0 or text in knownTexts:
        text += u' '

      knownTexts |= set([text])

      print(('add_vote "%s" "info"' % text).encode('utf-8'))
      continue

    originalMapName = words[1]
    mapName = normalizeMapname(originalMapName)
    if len(words) > 2:
      mapperName = words[2]
    else:
      mapperName = ""
    bestTime = 0
    countFinishes = 0
    bestTeamRank = ""
    bestRank = ""
    pointsText = renderStars(int(words[0]))

    try:
      cur.execute("select Time from record_teamrace where Map = '%s' ORDER BY Time LIMIT 1;" % con.escape_string(originalMapName))
      bestTime = formatTime(cur.fetchone()[0])
    except:
      pass

    try:
      cur.execute("select count(Name) from (select distinct Name from record_race where Map = '%s') as r;" % con.escape_string(originalMapName))
      countFinishes = cur.fetchone()[0]
    except:
      pass

    textFinishes = str(countFinishes)
    if countFinishes < 10:
      textFinishes = u' ' + textFinishes

    if countFinishes == 0:
      text = (u' %s | %s ⚑' % (pointsText, textFinishes)).encode('utf-8')
    else:
      try:
        cur.execute("select Name from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY TIME LIMIT 1) as l) left join (select * from record_teamrace where Map = '%s') as r on l.ID = r.ID order by Name;" % (con.escape_string(originalMapName), con.escape_string(originalMapName)))
        bestTeamRank = escapeOption(textJoinNames(map(lambda x: x[0], cur.fetchall())))
      except:
        pass

      if bestTeamRank == "":
        try:
          cur.execute("select Name, Time from record_race where Map = '%s' ORDER BY TIME LIMIT 1;" % con.escape_string(originalMapName))
          row = cur.fetchone()
          bestRank = escapeOption(row[0])
          bestTime = formatTime(row[1])
        except:
          pass

        text = (u' %s | %s ⚑ | 1. %s (%s)' % (pointsText, textFinishes, bestRank, bestTime)).encode('utf-8')

        if len(text) > 63:
          d = 63 - len(text) - 3
          bestRank = truncate(bestRank, d) + "..."
          text = (u' %s | %s ⚑ | 1. %s (%s)' % (pointsText, textFinishes, bestRank, bestTime)).encode('utf-8')

      else:
        text = (u' %s | %s ⚑ | 1. %s (%s)' % (pointsText, textFinishes, bestTeamRank, bestTime)).encode('utf-8')

        if len(text) > 63:
          d = 63 - len(text) - 3
          bestTeamRank = truncate(bestTeamRank, d) + "..."
          text = (u' %s | %s ⚑ | 1. %s (%s)' % (pointsText, textFinishes, bestTeamRank, bestTime)).encode('utf-8')

    while text in knownTexts:
      text += " "

    knownTexts |= set([text])

    if not mapperName:
      mbMapperName = ""
    else:
      mbMapperName = " by %s" % mapperName

    print 'add_vote "%s%s" "change_map \\"%s\\""' % (originalMapName, mbMapperName, originalMapName)
    print 'add_vote "%s" "info"' % text

    points = globalPoints(server, int(words[0]))
    mbS = 's'
    if points == 1:
      mbS = ''

    motdMap = '│ %s%s\\n│ Difficulty: %s (%d Point%s)' % (originalMapName, mbMapperName, pointsText, points, mbS)

    with open('data/maps/%s.map.cfg' % originalMapName, 'w') as cfg:
      #cfg.write(execString + "\n")
      cfg.write(motdSkeleton % (serverStrings[server], localString, motdMap, motdNews))
