from flask import render_template, request, redirect, url_for, session, flash
from passlib.hash import sha256_crypt
import cgi, gc, wtforms
from dbdata.connectionDB import connection
import os
import timeago, datetime

def loginFunc():
    username = request.form['username']
    password_candidate = request.form['password']
    # searching for username in database if exists
    cur, conn = connection()
    cur.execute("""SELECT id,password,theme,layout,Admin,Registered FROM users WHERE username = %s """, [username])
    data = cur.fetchone()
    cur.close()
    conn.close()
    if data is None:
        return ErrorLogin(1, username) 
    password = data['password']
    if sha256_crypt.verify(password_candidate, password):
        # fetching data
        theme = data['theme']
        layout = data['layout']
        sqlid = data['id']
        Admin = data['Admin']
        since = data['Registered']
        # asign data
        session['logged_in'] = True
        session['username'] = username
        session['theme'] = theme
        session['layout'] = layout
        session['sqlid'] = sqlid
        session['Admin'] = Admin
        session['since'] = since
        # avatar vars
        #avatars = os.listdir('static/images')
        playersqlid = session['sqlid']
        #avatarFound = False
        #for avatar in avatars:
            #a,b = avatar.split(".")
            #if int(a) == int(playersqlid):
                #print(avatar)
                #session['avatar'] = avatar
                #avatarFound = True
                #break
        #if avatarFound == False:
        session['avatar'] = '2.png'
    else:
        return ErrorLogin(2, username)
    # in caz ca trece de toate conditiile
    flash(u'Login successfully!', 'success')
    return redirect(url_for('index'))

def ErrorLogin(error, username):
    if error == 1:
        message = 'This account (%s) is not in our database.' % username
    elif error == 2:
        message = 'The password for %s is incorrect.' % username
    return render_template('login.html', message = message)
