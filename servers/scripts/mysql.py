import MySQLdb as mdb
import requests
import sys
import os

def mysqlConnect():
  if sys.version_info[0] == 3:
    return mdb.connect(
      os.environ.get("DDNET_MYSQL_HOST", '127.0.0.1'),
      os.environ.get("DDNET_MYSQL_USERNAME", 'teeworlds'),
      os.environ.get("DDNET_MYSQL_PASSWORD", 'SECRETSQL'),
      os.environ.get("DDNET_MYSQL_DATABASE", 'teeworlds'),
      charset='utf8mb4'
    )
  else:
    return mdb.connect(
      os.environ.get("DDNET_MYSQL_HOST", '127.0.0.1'),
      os.environ.get("DDNET_MYSQL_USERNAME", 'teeworlds'),
      os.environ.get("DDNET_MYSQL_PASSWORD", 'SECRETSQL'),
      os.environ.get("DDNET_MYSQL_DATABASE", 'teeworlds'),
    )

def postDiscord(msg):
  requests.post('https://discordapp.com/api/webhooks/%s' % os.environ.get("DDNET_DISCORD_WEBHOOK1", 'SECRETHOOK'), json={'content': msg, 'allowed_mentions': {'parse': []}})

def postDiscordRecords(msg):
  requests.post('https://discordapp.com/api/webhooks/%s' % os.environ.get("DDNET_DISCORD_WEBHOOK2", 'SECRETHOOK2'), json={'content': msg, 'allowed_mentions': {'parse': []}})
