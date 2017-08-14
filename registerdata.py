from flask import render_template, request, redirect, url_for, flash
from passlib.hash import sha256_crypt
import cgi, wtforms
from dbdata.connectionDB import connection
import gc

def registerFunc():
    username = request.form['username']
    email = request.form['email']
    # searching for username in database if exists
    cur, conn = connection()
    cur.execute("""SELECT username FROM users WHERE username = %s """, [username])
    data = cur.fetchone()
    cur.close()
    conn.close()
    if data is not None:
        return ErrorRegister(1)
    print(data)
    password = request.form['password']
    passretype = request.form['passretype']
    if password == passretype:
        password = sha256_crypt.encrypt((str(password)))
    else:
        return ErrorRegister(3)
    # in caz ca trece de toate conditiile
    return RegisterSuccess(username, password, email)

def RegisterSuccess(username, password, email):
    # insert data to database
    cur, conn = connection()
    sql = """INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"""
    cur.execute(sql, (username, password, email))
    #closing
    conn.commit()
    cur.close()
    conn.close()
    gc.collect()
    flash(u'Your account (%s) has been created! You can log in now.' % (username), 'success')
    return redirect(url_for('index'))


def ErrorRegister(error):
    if error == 1:
        message = 'This name is already registered. Pick another name.'
    elif error == 2:
        message = 'This email is already registered. Pick another email.'
    elif error == 3:
        message = 'Both passwords must match in order to procced'
    elif error == 4:
        message = 'test'
    return render_template('register.html', message = message)
