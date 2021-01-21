import MySQLdb as mdb
import requests
import sys

def mysqlConnect():
  if sys.version_info[0] == 3:
    return mdb.connect(
      '127.0.0.1',
      'teeworlds',
      'SECRETSQL',
      'teeworlds',
      charset='utf8mb4'
    )
  else:
    return mdb.connect(
      '127.0.0.1',
      'teeworlds',
      'SECRETSQL',
      'teeworlds'
    )

def postDiscord(msg):
  requests.post('https://discordapp.com/api/webhooks/SECRETHOOK', json={'content': msg, 'allowed_mentions': {'parse': []}})

def postDiscordRecords(msg):
  requests.post('https://discordapp.com/api/webhooks/SECRETHOOK2', json={'content': msg, 'allowed_mentions': {'parse': []}})
