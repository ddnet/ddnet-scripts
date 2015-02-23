import MySQLdb as mdb
def mysqlConnect():
  return mdb.connect(
    'localhost',
    'teeworlds',
    'dmd(n9=1mMkvnkd())99',
    'teeworlds'
  )
