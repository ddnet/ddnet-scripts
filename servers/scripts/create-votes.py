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
  'Insane'   : '                Insane Server',
  'Dummy'    : '                Dummy Server',
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
    #bestTime = ""
    countFinishes = 0
    countTees = 0
    averageTime = ""
    topTime = ""
    worstTime = ""
    releaseDate = ""
    #bestTeamRank = ""
    #bestRank = ""
    pointsText = renderStars(int(words[0]))

    #try:
    #  cur.execute("select Time from record_teamrace where Map = '%s' ORDER BY Time LIMIT 1;" % con.escape_string(originalMapName))
    #  bestTime = formatTime(cur.fetchone()[0])
    #except:
    #  pass

    try:
      cur.execute("select count(distinct Name), count(*) from record_race where Map = '%s';" % con.escape_string(originalMapName))
      line = cur.fetchone()
      countFinishes = line[0]
      countFinishesTotal = line[1]
    except:
      pass

    try:
      cur.execute("select avg(Time), min(Time), max(Time) from record_race where Map = '%s';" % con.escape_string(originalMapName))
      line = cur.fetchone()
      averageTime = formatTime(line[0])
      topTime = formatTime(line[1])
      worstTime = formatTime(line[2])
    except:
      pass

    try:
      cur.execute("select Timestamp from record_race where Map = '%s';" % con.escape_string(originalMapName))
      releaseDate = cur.fetchone()[0].strftime('%Y-%m-%d')
    except:
      pass

    textFinishes = str(countFinishes)
    if countFinishes < 10:
      textFinishes = u' ' + textFinishes

    if countFinishes == 0:
      text = (u' %s | %s ⚑' % (pointsText, textFinishes)).encode('utf-8')
    else:
      #try:
      #  cur.execute("select Name from ((select distinct ID from record_teamrace where Map = '%s' ORDER BY TIME LIMIT 1) as l) left join (select * from record_teamrace where Map = '%s') as r on l.ID = r.ID order by Name;" % (con.escape_string(originalMapName), con.escape_string(originalMapName)))
      #  bestTeamRank = escapeOption(textJoinNames(map(lambda x: x[0], cur.fetchall())))
      #except:
      #  pass

      #if bestTeamRank == "":
      #  try:
      #    cur.execute("select Name, Time from record_race where Map = '%s' ORDER BY TIME LIMIT 1;" % con.escape_string(originalMapName))
      #    row = cur.fetchone()
      #    bestRank = escapeOption(row[0])
      #    bestTime = formatTime(row[1])
      #  except:
      #    pass

      text = (u' %s | %s ⚑ | %s ◷' % (pointsText, textFinishes, averageTime)).encode('utf-8')

        #if len(text) > 63:
        #  d = 63 - len(text) - 3
        #  bestRank = truncate(bestRank, d) + "..."
        #  text = (u' %s | %s ⚑ | 1. %s (%s)' % (pointsText, textFinishes, bestRank, bestTime)).encode('utf-8')

      #else:
      #  text = (u' %s | %s ⚑ | 1. %s (%s)' % (pointsText, textFinishes, bestTeamRank, bestTime)).encode('utf-8')

      #  if len(text) > 63:
      #    d = 63 - len(text) - 3
      #    bestTeamRank = truncate(bestTeamRank, d) + "..."
      #    text = (u' %s | %s ⚑ | 1. %s (%s)' % (pointsText, textFinishes, bestTeamRank, bestTime)).encode('utf-8')

    while text in knownTexts:
      text += " "

    knownTexts |= set([text])

    if not mapperName:
      mbMapperName = ""
      mapperText = ""
    else:
      mbMapperName = " by %s" % mapperName
      mapperText = "\\n│ Mapper: %s" % mapperName


    print 'add_vote "%s%s" "change_map \\"%s\\""' % (originalMapName, mbMapperName, originalMapName)
    print 'add_vote "%s" "info"' % text

    points = globalPoints(server, int(words[0]))
    mbS = 's'
    if points == 1:
      mbS = ''

    if releaseDate:
      releaseDateText = "\\n│ Released on %s" % releaseDate
    else:
      releaseDateText = ""

    if topTime:
      topTimeText = "\\n│ Top Time: %s" % topTime
    else:
      topTimeText = ""

    if averageTime:
      averageTimeText = "\\n│ Average Time: %s" % averageTime
    else:
      averageTimeText = ""

    if worstTime:
      worstTimeText = "\\n│ Worst Time: %s" % worstTime
    else:
      worstTimeText = ""

    motdMap = '│ Map: %s%s\\n│ Difficulty: %s (%d Point%s)%s\\n│ %d finishes by %d tees%s%s%s' % (originalMapName, mapperText, pointsText, points, mbS, releaseDateText, countFinishesTotal, countFinishes, topTimeText, averageTimeText, worstTimeText)

    with open('maps/%s.map.cfg' % originalMapName, 'w') as cfg:
      #cfg.write(execString + "\n")
      cfg.write(motdSkeleton % (serverStrings[server], localString, motdMap))
