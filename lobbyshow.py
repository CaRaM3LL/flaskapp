from flask import Flask, render_template, url_for, redirect, flash, session
from dbdata.connectionDB import connection
import config

if config.test is None:
    import sys
    sys.path.append('/home/Husse6/.virtualenvs/myvirtualenv/lib/python3.6/site-packages')

import timeago, datetime

def LobbyShow(idlobby):
    now = datetime.datetime.now()
    cur, conn = connection()
    # data
    cur.execute("SELECT * FROM lobbies WHERE id = %s", [idlobby])
    lobbyname = cur.fetchone()
    lobbyname['created'] = time_converted = timeago.format(lobbyname['created'], now)
    # data
    cur.execute("SELECT * FROM lobby_data WHERE idlobby = %s ORDER BY joined DESC", [idlobby])    
    data = cur.fetchall()
    # logs
    cur.execute("SELECT text, date FROM lobby_logs WHERE idlobby = %s ORDER BY date DESC", [idlobby])    
    data_logs = cur.fetchall()
    for time2 in data_logs:
        time2['date'] = time_converted = timeago.format(time2['date'], now)
    # close
    cur.close()
    conn.close()
    joined = False
    for time in data:
        time['joined'] = time_converted = timeago.format(time['joined'], now)
        if 'logged_in' in session:
            if session['sqlid'] == time['membersqlid']:
                joined = True
    return render_template('lobby.html',
                           data = data, lobbyname = lobbyname,
                           joined = joined, data_logs = data_logs
                           )
                                                                                    
