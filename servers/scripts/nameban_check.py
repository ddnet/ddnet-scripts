#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys

reload(sys)
sys.setdefaultencoding('utf8')


def levenshtein_distance(string1, string2):
    if len(string1) > len(string2):
        string1, string2 = string2, string1

    distances = range(len(string1) + 1)
    for y, char2 in enumerate(string2):
        distances_ = [y+1]
        for x, char1 in enumerate(string1):
            if char1 == char2:
                distances_.append(distances[x])
            else:
                distances_.append(1 + min((distances[x], distances[x+1], distances_[-1])))
        distances = distances_

    return distances[-1]


def main():
    if len(sys.argv) != 4:
        print('Incorrect usage: <name> <distance> <is_substring>')
        return

    name = sys.argv[1].lower()
    distance = int(sys.argv[2])
    is_substring = int(sys.argv[3])

    con = mysqlConnect()

    with con:
        cur = con.cursor()
        cur.execute("set names 'utf8mb4';")

        cur.execute('SELECT Name, Points FROM record_points ORDER BY Points DESC;')
        rows = cur.fetchall()

    names = []
    for name_, points in rows:
        name_ = name_.strip()
        if levenshtein_distance(name, name_.lower()) <= distance or (is_substring and name in name_.lower()):
            names.append('%r %d pts' % (name_, points))

    print('\n'.join(names))


if __name__ == '__main__':
    main()
