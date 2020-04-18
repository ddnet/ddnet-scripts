import MySQLdb as mdb
import requests
def mysqlConnect():
  return mdb.connect(
    '127.0.0.1',
    'teeworlds',
    'SECRETSQL',
    'teeworlds'
  )

def postDiscord(msg):
  requests.post('https://discordapp.com/api/webhooks/SECRETHOOK', json={'content': msg})

def postDiscordRecords(msg):
  requests.post('https://discordapp.com/api/webhooks/SECRETHOOK2', json={'content': msg})
