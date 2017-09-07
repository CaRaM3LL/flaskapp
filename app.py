from flask import Flask, render_template, request, flash, session, redirect, url_for
from registerdata import registerFunc
from logindata import loginFunc
from dashboard import dashboardFunc
from dbdata.connectionDB import connection
import config
from reportshow import ReportShow
from flask_uploads import UploadSet, configure_uploads, IMAGES
from lobbyshow import LobbyShow

if config.test is None:
    import sys
    sys.path.append('/home/Husse6/.virtualenvs/myvirtualenv/lib/python3.6/site-packages')

import gc
import timeago, datetime
import os
from werkzeug import secure_filename

UPLOAD_FOLDER = 'static/images/'

app = Flask(__name__)
app.secret_key='secret11'


#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

###
@app.route('/')
def index():
    return dashboardFunc()

###
@app.route('/register', methods=['GET', 'POST'])
def reg():
    # in cazul in care este logat si se duce la register
    if 'logged_in' in session:
        return redirect(url_for('index'))
    else:
        if request.method == 'GET':
            return render_template('register.html')
        else:
            return registerFunc()

###
@app.route('/login', methods=['GET', 'POST'])
def login():
    # in cazul in care este logat si se duce la login
    if 'logged_in' in session:
        return redirect(url_for('index'))
    else:
        if request.method == 'GET':
            return render_template('login.html')
        else:
            return loginFunc()

###
@app.route('/logout')
def profile():
    if 'logged_in' in session:
        session.clear()
        flash(u'You have been logout from your account', 'warning')
    else:
        flash(u'You must be logged for this.', 'danger')
        return redirect(url_for('index'))
    return redirect(url_for('index'))

###
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'logged_in' in session:
        if request.method == 'POST':
            if 'Item_1' and 'Item_2' in request.form:   
                newtheme = request.form.get('Item_1')
                layout = request.form.get('Item_2')
                if newtheme and layout:
                    session['theme'] = newtheme
                    session['layout'] = layout
                    flash(u'Changes saved!', 'info')
                    # save
                    cur, conn = connection()
                    cur.execute("UPDATE users SET Theme = %s, Layout = %s WHERE id = %s", (newtheme, layout, session['sqlid']))
                    conn.commit()
                    cur.close()
                    conn.close()
                else:
                    flash(u'You must complete the fields.', 'warning')
            #elif 'file' in request.files:
                # check image and delete if already ..
                #avatars = os.listdir('static/images')
                #avatarFound = False
                #for avatar in avatars:
                    #a,b = avatar.split(".")
                    #if int(a) == int(session['sqlid']):
                        #avatarFound = True
                        #os.remove(os.path.join("static/images", avatar))
                        #break
                # saving image
                #file = request.files['file']
                #filename = file.filename
                #a2,b2 = filename.split(".")
                #file_new_name = str(session['sqlid']) + '.' + b2
                #filename2 = photos.save(file, None, file_new_name)
                #session['avatar'] = filename2
                #flash(u'Image saved!', 'success')
            elif 'Phone' and 'Location' in request.form:
                phone = request.form['Phone']
                location = request.form['Location']
                about = request.form['About']
                if phone:
                    cur, conn = connection()
                    cur.execute("UPDATE users SET Phone = %s WHERE id = %s", (phone, session['sqlid']))
                    conn.commit()
                    cur.close()
                    conn.close()
                    flash(u'Phone updated!', 'success') 
                if location:
                    cur, conn = connection()
                    cur.execute("UPDATE users SET Location = %s WHERE id = %s", (location, session['sqlid']))
                    conn.commit()
                    cur.close()
                    conn.close()
                    flash(u'Location updated!', 'success')
                if about:
                    cur, conn = connection()
                    cur.execute("UPDATE users SET About = %s WHERE id = %s", (about, session['sqlid']))
                    conn.commit()
                    cur.close()
                    conn.close()
                    flash(u'About updated!', 'success')
    else:
        flash(u'You must be logged for this.', 'danger')
        return redirect(url_for('index'))
    cur, conn = connection()
    cur.execute("""SELECT Phone, Location, About FROM users WHERE username = %s""", [session['username']])
    data = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('settings.html', data = data)

###

###
@app.route('/profile-<username>', methods=['GET', 'POST'])
def userprofile(username):
    cur, conn = connection()
    cur.execute("""SELECT username, Phone, Location, About FROM users WHERE username = %s""", [username])
    data = cur.fetchone()
    if data is None:
        flash(u'This username is not registered.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        if 'reply' in request.form:
            comment = request.values['reply']
            if comment:
                sql = """INSERT INTO profile_comments (username, byusername, comment) VALUES (%s, %s, %s)"""
                cur.execute(sql, (username, session['username'], comment))
                #closing
                conn.commit()
                gc.collect()
                flash(u'You posted a comment on %s profile.' % (username), 'success')
    cur.execute("""SELECT * FROM profile_comments WHERE username = %s ORDER BY date DESC""", [username])
    data_comments = cur.fetchall()
    cur.close()
    conn.close()
    now = datetime.datetime.now()
    for time in data_comments:
        time['date'] = time_converted = timeago.format(time['date'], now)
    return render_template('profiles.html', data = data, data_comments = data_comments)

###
@app.route('/report')
def report():
    cur, conn = connection()
    cur.execute("SELECT * FROM report ORDER BY date DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    if data:
        rows = cur.rowcount
        closed = 0
        opened = 0
        for row in data:
            status = row['status']
            if status == 1:
                closed += 1
            elif status == 0:
                opened += 1
        now = datetime.datetime.now()
        for time in data:
            time['date'] = time_converted = timeago.format(time['date'], now)
        return render_template('report.html',
                               data = data, rows = rows,
                               closed = closed, opened = opened
                               )
    else:
        flash(u'No reports found.', 'success')
        return render_template('report.html')

###
@app.route('/report-<idreport>', methods=['GET', 'POST'])
def reportid(idreport):
    cur, conn = connection()
    if request.method == 'POST':
        if 'opened' in request.form:
            cur.execute("""UPDATE report SET status = '0' WHERE id = %s""", [idreport])
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
            flash(u'You opened ticket number #%s.' % (idreport), 'warning')
        elif 'closed' in request.form:
            cur.execute("""UPDATE report SET status = 1 WHERE id = %s""", [idreport])
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
            flash(u'You closed ticket number #%s.' % (idreport), 'warning')
        elif 'reply' in request.form:
            comment = request.values['reply']
            sql = """INSERT INTO report_comments (username, reportid, comment) VALUES (%s, %s, %s)"""
            cur.execute(sql, (session['username'], idreport, comment))
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
            flash(u'You posted a reply in ticket #%s.' % (idreport), 'success')
        elif 'delete' in request.form:
            cur.execute("""DELETE FROM report WHERE id = %s""", [idreport])
            cur.execute("""DELETE FROM report_comments WHERE reportid = %s""", [idreport])
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
            flash(u'You deleted ticket number #%s.' % (idreport), 'warning')
            return redirect(url_for('report'))
        elif 'deletecomm' in request.form:
            idcomm = request.values['deletecomm']
            cur.execute("""DELETE FROM report_comments WHERE id = %s""", [idcomm])
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
            flash(u'You deleted comment id #%s from reportid #%s.' % (idcomm, idreport), 'warning')
            print(idcomm)
    return ReportShow(idreport)
    

###
@app.route('/posting', methods=['GET', 'POST'])
def postreport():
    if 'logged_in' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            # insert data to database
            cur, conn = connection()
            sql = """INSERT INTO report (username, title, content) VALUES (%s, %s, %s)"""
            cur.execute(sql, (session['username'], title, content))
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
            flash(u'You posted a problem in this forum.', 'success')
            return redirect(url_for('report'))
        elif request.method == 'GET':
            print('get')
    else:
        flash(u'You must be logged for this.', 'danger')
        return redirect(url_for('index'))
    return render_template('postreport.html')

###
@app.route('/updatepost', methods=['GET', 'POST'])
def updatepost():
    if 'logged_in' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            # insert data to database
            cur, conn = connection()
            sql = """INSERT INTO updates (username, title, content) VALUES (%s, %s, %s)"""
            cur.execute(sql, (session['username'], title, content))
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
            flash(u'You posted a new update.', 'success')
            return redirect(url_for('updates'))
    else:
        flash(u'You must be logged for this.', 'danger')
        return redirect(url_for('index'))
    return render_template('updatepost.html')

###
@app.route('/updates')
def updates():
    cur, conn = connection()
    cur.execute("SELECT * FROM updates ORDER BY date DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    if data:
        now = datetime.datetime.now()
        for time in data:
            time['date'] = time_converted = timeago.format(time['date'], now)
        return render_template('updates.html',
                               data = data
                               )
    else:
        flash(u'No updates found.', 'success')
        return render_template('updates.html')

###
@app.route('/lobbies')
def lobbies():
    cur, conn = connection()
    cur.execute("SELECT * FROM lobbies ORDER BY created DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    now = datetime.datetime.now()
    for time in data:
        time['created'] = time_converted = timeago.format(time['created'], now)
    return render_template('lobbies.html', data = data)

###
@app.route('/lobbies-<idlobby>', methods=['GET', 'POST'])
def lobby(idlobby):
    cur, conn = connection()
    if request.method == 'POST':
        if 'join' in request.form:
            sql = "INSERT INTO lobby_data (idlobby, membername, membersqlid) VALUES (%s, %s, %s)"
            cur.execute(sql, (idlobby, session['username'], session['sqlid']))
            flash(u'You joined in this lobby.', 'success')
            # log for lobby
            text = '%s joined this lobby.' % session['username']
            cur.execute("INSERT INTO lobby_logs (idlobby, text) VALUES (%s, %s)", (idlobby, text))
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
        elif 'leave' in request.form:
            sql = "DELETE FROM lobby_data WHERE membersqlid = %s and idlobby = %s"
            cur.execute(sql, (session['sqlid'], idlobby))
            flash(u'You left from this lobby.', 'danger')
            # log for lobby
            text = '%s left this lobby.' % session['username']
            cur.execute("INSERT INTO lobby_logs (idlobby, text) VALUES (%s, %s)", (idlobby, text))
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
        elif 'changerule' in request.form:
            print('changerule')
        elif 'resetlogs' in request.form:
            sql = "DELETE FROM lobby_logs WHERE idlobby = %s"
            cur.execute(sql, [idlobby])
            flash(u'You deleted the logs from this lobby.', 'success')
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
        elif 'deletelobby' in request.form:
            sql = "DELETE FROM lobby_logs WHERE idlobby = %s"
            cur.execute(sql, [idlobby])
            sql = "DELETE FROM lobbies WHERE id = %s"
            cur.execute(sql, [idlobby])
            sql = "DELETE FROM lobby_data WHERE idlobby = %s"
            cur.execute(sql, [idlobby])
            flash(u'You deleted the lobby.', 'success')
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
            return redirect(url_for('lobbies'))
    return LobbyShow(idlobby)

###
@app.route('/createlobby', methods=['GET', 'POST'])
def createlobby():
    if 'logged_in' in session:
        if request.method == 'POST':
            lobbyname = request.form['lobbyname']
            lobbyrule = request.form['lobbyrule']
            cur, conn = connection()
            sql = "INSERT INTO lobbies (creator, lobbyname, Rule) VALUES (%s, %s, %s)"
            cur.execute(sql, (session['sqlid'], lobbyname, lobbyrule))
            #closing
            conn.commit()
            cur.close()
            conn.close()
            gc.collect()
            flash(u'Lobby created!', 'success')
            return redirect(url_for('lobbies'))
    else:
        flash(u'You must be logged for this.', 'danger')
        return redirect(url_for('index'))
    return render_template('createlobby.html')
    
###
@app.errorhandler(404)
def error404(error):
    return render_template('404.html')

if __name__ == '__main__':
    if config.test:
        app.run(debug=True)
    else:
        app.run()
