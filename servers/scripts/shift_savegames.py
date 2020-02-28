#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ddnet import *
import sys

reload(sys)
sys.setdefaultencoding('utf8')

pos_values = (
    (46, 47),  # m_Pos
    (48, 49),  # m_PrevPos
    (52, 53),  # m_CorePos
    (60, 61),  # m_HookPos
    (64, 65),  # m_HookTeleBase
)

def shift_savegame(savegame, x=0, y=0):
    savegame = [l.split('\t') for l in savegame.split('\n')]
    member_count = int(savegame[0][1])

    for l in savegame[1:member_count+1]:
        for pos_x, pos_y in pos_values:
            l[pos_x] = str(int(l[pos_x]) + 32 * x)
            l[pos_y] = str(int(l[pos_y]) + 32 * y)

    return '\n'.join('\t'.join(l) for l in savegame)

def main():
    try:
        _, map_, x, y = sys.argv
    except ValueError:
        print('Wrong arguments: <map> <x> <y>')
        return

    try:
        x = int(x)
        y = int(y)
    except ValueError:
        print('<x> and <y> have to be numbers')
        return

    con = mysqlConnect()

    with con:
        cur = con.cursor()
        cur.execute('SET names "utf8mb4";')

        cur.execute('SELECT Savegame, code FROM record_saves WHERE Map = %s;', (map_,))
        rows = cur.fetchall()

        for savegame, code in rows:
            cur.execute('UPDATE record_saves SET Savegame = %s WHERE Map = %s AND code = %s;', (shift_savegame(savegame, x=x, y=y), map_, code))

    print('Updated %d row(s)' % len(rows))

if __name__ == '__main__':
    main()
