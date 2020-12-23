from flask import Flask 
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_mysqldb import MySQL
import os
import datetime
import DbConf
import Admin
app= Flask(__name__)
mysql = MySQL(app)
app.config['MYSQL_HOST'] = DbConf.host
app.config['MYSQL_USER'] = DbConf.user
app.config['MYSQL_PASSWORD'] = DbConf.passkey
app.config['MYSQL_DB'] = DbConf.database

app.secret_key = os.urandom(24)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('Booking details.html', data = 0)

@app.route('/check',methods = ['POST'])
def do_admin_login():
    if request.form['password'] == Admin.PassKey and request.form['username'] == Admin.username:
        session ['logged_in'] = True
        return home()
    else:
        return render_template('loginError.html')

@app.route("/logout")
def logout():
    logged_in = session.get('logged_in')
    session['logged_in'] = False
    return home()

@app.route('/CheckAvailability', methods = ['POST'])
def CheckAvailability():
    cursor = mysql.connection.cursor()
    currCheckinDate=request.form['CheckinDate']
    currCheckoutDate=request.form['CheckoutDate']
    session['currCheckinDate'] = currCheckinDate
    session['currCheckoutDate'] = currCheckoutDate
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    if currCheckoutDate <= currCheckinDate or currCheckinDate < today:
        error = 'Invalid dates'
        return render_template('Booking details.html', data = error)
        pass
    else:
        query = "select RoomNo from visitors where not (('"+currCheckinDate+"'> CheckoutDate) or ('"+currCheckoutDate+"'< CheckinDate) or ('" +currCheckinDate +"'= CheckoutDate) or ('"+ currCheckoutDate +"' = CheckinDate) )"
        query2 = "select id , RoomType from room where RoomNo not in("+query+");"
        cursor.execute(query2)
        if cursor.rowcount !=0:
            data = cursor.fetchall()
            return render_template('Room_Book.html', data = data)
            pass
        else:
            return "No Rooms Available"

@app.route('/book', methods = ['POST'])
def book():
    room = request.form.getlist('room')
    session['room'] = room
    return render_template('/GetDetails.html',)
    
@app.route('/Checkin', methods=['POST'])
def Checkin():
    cursor = mysql.connection.cursor()
    room = session.get('room')
    currCheckinDate = session.get('currCheckinDate')
    currCheckoutDate = session.get('currCheckoutDate')
    name = request.form['Name']
    gender = request.form['gender']
    phone = request.form['Phone']
    ID = request.form['idproof']
    for i in room:
        W_query = "insert into visitors (Name,PhoneNo,VisitorsId,CheckinDate,CheckoutDate,RoomNo,Gender) values('"+str(name)+" ', '"+str(phone)+"' , '"+str(ID)+"', '" +str(currCheckinDate)+"', ' "+str(currCheckoutDate)+"', ' "+str(i)+"','"+str(gender[0])+"');"
        cursor.execute(W_query)
        mysql.connection.commit()
    return render_template('Ticket_Gen.html', data = room)

if __name__ == '__main__':
    app.run()