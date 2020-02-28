#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from collections import defaultdict

from ddnet import *


def main():
    con = mysqlConnect()

    with con:
        cur = con.cursor()
        cur.execute('SET NAMES "utf8mb4";')

        query = 'SELECT record_race.Map, record_race.Time, record_race.Name FROM record_race INNER JOIN record_maps ON record_race.Map = record_maps.Map WHERE record_race.Timestamp >= "2018-01-01" AND (record_maps.Server = "Solo" OR record_maps.Server = "Dummy");'
        cur.execute(query)
        ranks = cur.fetchall()

        results = defaultdict(lambda: defaultdict(list))
        for map_, time, name in ranks:
            results[map_][time].append(name)

        results = [[map_, time, names] for map_, data in results.items() for time, names in data.items() if len(names) > 1]
        results = sorted(results, key=lambda r: (r[0], r[1]))

        print('\n'.join(' | '.join([map_, str(time), ', '.join(n for n in names)]) for map_, time, names in results))

if __name__ == '__main__':
    main()
