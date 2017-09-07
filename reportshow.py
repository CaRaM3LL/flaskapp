from flask import Flask, render_template, url_for, redirect, flash
from dbdata.connectionDB import connection
import config

if config.test is None:
    import sys
    sys.path.append('/home/Husse6/.virtualenvs/myvirtualenv/lib/python3.6/site-packages')

import timeago, datetime

def ReportShow(idreport):
    cur, conn = connection()
    cur.execute("""SELECT * FROM report WHERE id = %s""", [idreport])
    data = cur.fetchone()
    if data is None:
        flash(u'This report id was deleted or not exist.', 'danger')
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    cur.execute("""SELECT id,username,comment,date FROM report_comments WHERE reportid = %s""", [idreport])
    comments = cur.fetchall()
    rows = cur.rowcount
    cur.close()
    conn.close()
    now = datetime.datetime.now()
    for time in comments:
        time['date'] = time_converted = timeago.format(time['date'], now)
    return render_template('reportid.html', data = data, comments = comments,
                                            rows = rows)
                                                                                    
