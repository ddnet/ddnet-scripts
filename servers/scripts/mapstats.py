#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ddnet import *
import sys
import msgpack
import locale
from html import escape
from datetime import datetime, timedelta
from time import strftime
from collections import defaultdict, OrderedDict
from dateutil.relativedelta import relativedelta
from contextlib import nullcontext

locale.setlocale(locale.LC_ALL, 'en_US')

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
tf = open(tmpname, 'w', encoding='utf-8')
print(header("Map Statistics", "", ""), file=tf)
print("""<div class="block">
<h2>Map Statistics</h2>
%s
<p class="toggle">Refreshed: %s</p>
</div>
</section>
</article>
</body>
</html>""" % (menuText, strftime("%Y-%m-%d %H:%M")), file=tf)
tf.close()
os.rename(tmpname, filename)

# Finishes
con = mysqlConnect()
with nullcontext():
  cur = con.cursor()
  cur.execute("set names 'utf8mb4';")
  cur.execute("SET SESSION max_statement_time=0")  # batch job: allow long queries (global 60s net stays for web/game)

  for typ in types:
    filename = "%s/stats/maps/%s/index.html" % (webDir, typ.lower())
    tmpname = "%s/stats/maps/%s/index.%d.tmp" % (webDir, typ.lower(), os.getpid())
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
      os.makedirs(directory)

    tf = open(tmpname, 'w', encoding='utf-8')
    print(header("%s Server - Map Statistics" % typ, menuText, ""), file=tf)
    print('<div class="block">', file=tf)
    print('<h2>%s Server - Map Statistics</h2>' % typ, file=tf)
    print('<div style="overflow-x: auto;">', file=tf)
    print('<table style="border-collapse: separate; border-spacing: 0; margin: 0;">', file=tf)
    print('<tr style="text-align: center;"><th>Date</th><th>#1</th><th>#2</th><th>#3</th><th>#4</th><th>#5</th></tr>', file=tf)

    today = datetime.today();
    timestamp = datetime(today.year, today.month, 1)
    while timestamp >= datetime(2013, 7, 1):
      nextTimestamp = timestamp + relativedelta(months=1)
      print("<tr><td>%d-%02d</td>" % (timestamp.year, timestamp.month), file=tf)
      num = 5
      cur.execute('select record_race.Map, count(*) as C from record_race inner join record_maps on record_race.Map = record_maps.Map where record_race.Timestamp >= "%s" and record_race.Timestamp < "%s" and record_maps.Server = "%s" group by record_race.Map order by C desc limit %d;' % (timestamp.strftime("%Y-%m-%d %H:%M:%S"), nextTimestamp.strftime("%Y-%m-%d %H:%M:%S"), typ, num))
      rows = cur.fetchall()
      for i in range(num):
        if i < len(rows):
          row = rows[i]
          print('  <td title="%s: %d finishes"><a href="%s"><img src="/ranks/maps/%s.png" width="180" height="112" alt="%s" /></a></td>' % (escape(row[0]), row[1], mapWebsite(row[0]), normalizeMapname(row[0]), escape(row[0])), file=tf)
        else:
          print('  <td></td>', file=tf)
      print('</tr>', file=tf)
      timestamp -= relativedelta(months=1)
    print('</table></div></div>', file=tf)
    print("""<p class="toggle">Refreshed: %s</p>
</section>
</article>
</body>
</html>""" % strftime("%Y-%m-%d %H:%M"), file=tf)
    tf.close()
    os.rename(tmpname, filename)
