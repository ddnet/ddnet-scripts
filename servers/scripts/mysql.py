import MySQLdb as mdb
import requests
def mysqlConnect():
  return mdb.connect(
    'localhost',
    'teeworlds',
    'SECRETSQL',
    'teeworlds'
  )

def postDiscord(msg):
  requests.post('https://discordapp.com/api/webhooks/SECRETHOOK', json={'content': msg})
