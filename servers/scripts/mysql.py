import MySQLdb as mdb
def mysqlConnect():
  return mdb.connect(
    'localhost',
    'teeworlds',
    'SECRETSQL',
    'teeworlds'
  )
