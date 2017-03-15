#!/usr/bin/env python3

from collections import namedtuple
import argparse
import pymysql

TeamRank = namedtuple('TeamRank', ['ID', 'Name', 'Map', 'Time', 'Timestamp'])

parser = argparse.ArgumentParser(__file__, description='Delete all ranks and teamranks of a specific player.')
parser.add_argument('user', type=str)
parser.add_argument('host', type=str)
parser.add_argument('database', type=str)
parser.add_argument('password', type=str)
parser.add_argument('--port', type=int, default=3306)
parser.add_argument('--prefix', type=str, default='record')
parser.add_argument('--socket', type=str, default=None)
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--restore', action='store_true')

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument('--player', type=str)
group.add_argument('--create-backup-tables', action='store_true')


args = parser.parse_args()


with pymysql.Connect(args.host, args.user, args.password, args.database, args.port, args.socket, charset='utf8') as cur:

    def execute(sql, mutating=True):
        if mutating:
            print(sql)
            if not args.dry_run:
                cur.execute(sql)
        else:
            cur.execute(sql)

    if args.create_backup_tables:
        execute("CREATE TABLE IF NOT EXISTS {prefix}_race_backup like {prefix}_race".format(prefix=args.prefix))
        execute("CREATE TABLE IF NOT EXISTS {prefix}_teamrace_backup like {prefix}_teamrace".format(prefix=args.prefix))
        exit()

    player_escaped = cur.connection.escape_string(args.player)
    if args.restore:
        execute("SELECT ID FROM %s_teamrace_backup WHERE Name = '%s'" % (args.prefix, player_escaped), mutating=False)    
    else:
        execute("SELECT ID FROM %s_teamrace WHERE Name = '%s'" % (args.prefix, player_escaped), mutating=False)
    IDS = [i[0].decode('utf-8') for i in cur.fetchall()]
    team_ranks = []
    for i in IDS:
        if args.restore:
            execute("SELECT ID, Name, Map, Time, Timestamp FROM %s_teamrace_backup WHERE ID = '%s'" % (args.prefix, i), mutating=False)
        else:
            execute("SELECT ID, Name, Map, Time, Timestamp FROM %s_teamrace WHERE ID = '%s'" % (args.prefix, i), mutating=False)
        for tr in cur.fetchall():
            team_ranks.append(TeamRank(tr[0].decode('utf-8'), cur.connection.escape_string(tr[1]), cur.connection.escape_string(tr[2]), *tr[3:]))

        if args.restore:
            execute("INSERT IGNORE INTO {prefix}_teamrace SELECT * FROM {prefix}_teamrace_backup WHERE ID = '{ID}'".format(prefix=args.prefix, ID=i))
            execute("DELETE FROM {prefix}_teamrace_backup WHERE ID = '{ID}'".format(prefix=args.prefix, ID=i))
        else:
            execute("INSERT IGNORE INTO {prefix}_teamrace_backup SELECT * FROM {prefix}_teamrace WHERE ID = '{ID}'".format(prefix=args.prefix, ID=i))
            execute("DELETE FROM {prefix}_teamrace WHERE ID = '{ID}'".format(prefix=args.prefix, ID=i))
    
    for tr in team_ranks:
        where_clause = "WHERE Map = '{Map}' and Name = '{Name}' and Timestamp > TIMESTAMPADD(MINUTE, -30, '{Timestamp}') and Timestamp < TIMESTAMPADD(MINUTE, 30, '{Timestamp}') and Time > {Time} - 0.01  and Time < {Time} + 0.01".format(
            prefix=args.prefix, Map=tr.Map, Name=tr.Name, Timestamp=tr.Timestamp, Time=tr.Time)

        if args.restore:
            execute("INSERT IGNORE INTO {prefix}_race SELECT * FROM {prefix}_race_backup {where}".format(prefix=args.prefix, where=where_clause))
            execute("DELETE FROM {prefix}_race_backup {where}".format(prefix=args.prefix, where=where_clause))
        else:
            execute("INSERT IGNORE INTO {prefix}_race_backup SELECT * FROM {prefix}_race {where}".format(prefix=args.prefix, where=where_clause))
            execute("DELETE FROM {prefix}_race {where}".format(prefix=args.prefix, where=where_clause))

    if args.restore:
        execute("INSERT IGNORE INTO {prefix}_race SELECT * FROM {prefix}_race_backup WHERE NAME = '{player}'".format(prefix=args.prefix, player=player_escaped))
        execute("DELETE FROM {prefix}_race_backup WHERE NAME = '{player}'".format(prefix=args.prefix, player=player_escaped))
    else:
        execute("INSERT IGNORE INTO {prefix}_race_backup SELECT * FROM {prefix}_race WHERE NAME = '{player}'".format(prefix=args.prefix, player=player_escaped))
        execute("DELETE FROM {prefix}_race WHERE NAME = '{player}'".format(prefix=args.prefix, player=player_escaped))
