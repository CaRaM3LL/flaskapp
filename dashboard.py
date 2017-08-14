from flask import render_template, flash, session
from dbdata.connectionDB import connection

def dashboardFunc():
    # aratam la toti o statistica generala
    cur, conn = connection()
    cur.execute("""SELECT * FROM users""")
    rows = cur.rowcount
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('home.html', rows = rows, data = data)
