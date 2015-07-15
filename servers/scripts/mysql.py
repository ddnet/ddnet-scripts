import MySQLdb as mdb
def mysqlConnect():
  return mdb.connect(
    'localhost',
    'teeworlds',
    'SECRETPASS',
    'teeworlds'
  )
