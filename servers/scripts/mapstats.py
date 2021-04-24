#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
import locale
from cgi import escape
from datetime import datetime, timedelta
from time import strftime
from collections import defaultdict, OrderedDict
from dateutil.relativedelta import relativedelta

locale.setlocale(locale.LC_ALL, 'en_US')
reload(sys)
sys.setdefaultencoding('utf8')

with open('/home/teeworlds/servers/all-types', 'r') as f:
  types = f.read().split()

menuText = '<ul>'
for type in types:
  menuText += '<li><a href="/stats/maps/%s/">%s Server</a></li>\n' % (type.lower(), type)
menuText += '</ul>'

filename = "%s/stats/maps/index.html" % (webDir)
tmpname = "%s/stats/maps/index.%d.tmp" % (webDir, os.getpid())
directory = os.path.dirname(filename)
if not os.path.exists(directory):
  os.makedirs(directory)
tf = open(tmpname, 'w')
print >>tf, header("Map Statistics", "", "")
print >>tf, """<div class="block">
<h2>Map Statistics</h2>
%s
<p class="toggle">Refreshed: %s</p>
</div>
</section>
</article>
</body>
</html>""" % (menuText, strftime("%Y-%m-%d %H:%M"))
tf.close()
os.rename(tmpname, filename)

# Finishes
con = mysqlConnect()
with con:
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")

  for typ in types:
    filename = "%s/stats/maps/%s/index.html" % (webDir, typ.lower())
    tmpname = "%s/stats/maps/%s/index.%d.tmp" % (webDir, typ.lower(), os.getpid())
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
      os.makedirs(directory)

    tf = open(tmpname, 'w')
    print >>tf, header("%s Server - Map Statistics" % typ, menuText, "")
    print >>tf, '<div class="block">'
    print >>tf, '<h2>%s Server - Map Statistics</h2>' % typ
    print >>tf, '<div style="overflow-x: auto;">'
    print >>tf, '<table style="border-collapse: separate; border-spacing: 0; margin: 0;">'
    print >>tf, '<tr style="text-align: center;"><th>Date</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>'

    today = datetime.today();
    timestamp = datetime(today.year, today.month, 1)
    while timestamp >= datetime(2013, 7, 1):
      nextTimestamp = timestamp + relativedelta(months=1)
      print >>tf, "<tr><td>%d-%02d</td>" % (timestamp.year, timestamp.month)
      num = 5
      cur.execute('select record_race.Map, count(*) as C from record_race inner join record_maps on record_race.Map = record_maps.Map where record_race.Timestamp >= "%s" and record_race.Timestamp < "%s" and record_maps.Server = "%s" group by record_race.Map order by C desc limit %d;' % (timestamp.strftime("%Y-%m-%d %H:%M:%S"), nextTimestamp.strftime("%Y-%m-%d %H:%M:%S"), typ, num))
      rows = cur.fetchall()
      for i in range(num):
        if i < len(rows):
          row = rows[i]
          print >>tf, '  <td title="%s: %d finishes"><a href="%s"><img src="/ranks/maps/%s.png" width="180" height="112" alt="%s" /></a></td>' % (escape(row[0]), row[1], mapWebsite(row[0]), normalizeMapname(row[0]), escape(row[0]))
        else:
          print >>tf, '  <td></td>'
      print >>tf, '</tr>'
      timestamp -= relativedelta(months=1)
    print >>tf, '</table></div></div>'
    print >>tf, """<p class="toggle">Refreshed: %s</p>
</section>
</article>
</body>
</html>""" % strftime("%Y-%m-%d %H:%M")
    tf.close()
    os.rename(tmpname, filename)
