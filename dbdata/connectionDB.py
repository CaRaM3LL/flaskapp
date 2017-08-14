import MySQLdb
import MySQLdb.cursors

def connection():
    conn = MySQLdb.connect(host = "localhost",
                           user = "root",
                           passwd = "",
                           db = "site database",
                           cursorclass=MySQLdb.cursors.DictCursor)
    cur = conn.cursor()
    return cur, conn
