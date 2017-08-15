import MySQLdb
import MySQLdb.cursors
import config

if config.test:
    host = "localhost"
    user = "root"
    passwd = ""
    db = "site database"
else:
    host = "Husse6.mysql.pythonanywhere-services.com"
    user = "Husse6"
    passwd = "Steaua21"
    db = "Husse6$site_database"
    

def connection():
    conn = MySQLdb.connect(host, user, passwd, db,
                           cursorclass=MySQLdb.cursors.DictCursor)
    cur = conn.cursor()
    return cur, conn
