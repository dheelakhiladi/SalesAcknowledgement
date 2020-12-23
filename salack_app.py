import waitress
from flask import Flask
from flask import Flask 
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for,Response
from flask_mysqldb import MySQL
import os
import datetime
import Admin
import DbConf
import hashlib
import requests
import pandas as pd
from random import randint
app = Flask(__name__)
app.secret_key = os.urandom(24)
mysql = MySQL(app)
app.config['MYSQL_HOST'] = DbConf.host
app.config['MYSQL_USER'] = DbConf.user
app.config['MYSQL_PASSWORD'] = DbConf.passkey
app.config['MYSQL_DB'] = DbConf.database

@app.route('/')
def home():
	if not session.get('AdminLoggedIn'):
		if not session.get('logged_in'):
			return render_template('loginSelector.html')
		else:
			return render_template('newEntry.html')
	else:
		return adminHome()
@app.route('/dplogin')
def dplogin():	
	if not session.get('AdminLoggedIn'):
		if not session.get('logged_in'):
			return render_template('login.html')
		else:
			return render_template('newEntry.html')
	else:
		return adminHome()

@app.route('/check',methods = ['POST'])
def do_user_login():
	h = hashlib.md5(request.form['password'].encode())
	hpwd = h.hexdigest()
	cursor = mysql.connection.cursor()
	query = "SELECT Password FROM deliveryPerson WHERE UserName='"+request.form['username']+"';"
	cursor.execute(query)
	if cursor.rowcount !=0:
		for row in cursor.fetchone():
			password = row
		cursor.close()
	else:
		return render_template("loginErrorReg.html")
	if hpwd == password:
		session['logged_in'] = True
		return home()
	else:
		return render_template("/loginError.html")
@app.route('/registerTemp')
def goto_register():
		return render_template('register.html')	
@app.route('/register',methods = ['POST'])
def do_user_registration():
	render_template('register.html')
	name = request.form['name']
	username = request.form['username']
	phnbr = int(request.form['Phnbr'])
	password = request.form['password']
	if name =="":
		return render_template("/RegError.html")
	if username=="":
		return render_template("/RegError.html")
	if phnbr <100000000:
		return render_template("/RegError.html")
	if password =="":
		return render_template("/RegError.html") 
	h = hashlib.md5(password.encode())
	hpwd = h.hexdigest()
	cursor = mysql.connection.cursor()
	query = "insert into deliveryPerson (Name,UserName,Password,Phone) values('"+str(name)+" ', '"+str(username)+"' , '"+str(hpwd)+"', '" +str(phnbr)+"');"
	try:
		cursor.execute(query)
		mysql.connection.commit()
		cursor.close()
	except:
		return render_template('/RegError.html')
	else:
		return render_template('/Registered.html')
@app.route('/sendOTP',methods = ['POST'])
def sendOTP():
	session['InvoiceNbr'] = request.form['InvoiceNbr']
	session['DOI'] = request.form['DOI']
	session['DelPh'] = request.form['DelPh']
	session['RecName'] = request.form['RecName']
	session['DOR'] = request.form['DOR'] 
	session['RecPh'] = request.form['RecPh']
	otp = randint(100000,1000000)
	session['otp'] = str(otp)
	print(otp)
	url = "https://www.fast2sms.com/dev/bulk"
	querystring = {"authorization":"BJxZ9aKWsoghHG7ATUYyf5P86qm14tOVIRQzdp3lwMjDcEnXrvVDsGi80lLTh2ug4tJqAn1aSIX7xPR9","sender_id":"FSTSMS","message":"Your OTP is"+otp+" for D.N. Agencies order Acknowledgement ","language":"english","route":"p","numbers":RecPh}
	headers = {
    	'cache-control': "no-cache"
	}
	response = requests.request("GET", url, headers=headers, params=querystring)
	return render_template('/enterOtp.html')
@app.route('/verifyOtp',methods = ['POST'])
def verifyOtp():
	otp_gen = session.get('otp')
	otp_ent = str(request.form['OTP'])
	print(otp_gen)
	print(otp_ent)
	if otp_gen == otp_ent:
		cursor = mysql.connection.cursor()
		query = "insert into sales (InvNbr,DOI,DelNbr,RecName,DOR,RecNbr,OTP) values('"+str(session.get('InvoiceNbr'))+" ', '"+str(session.get('DOI'))+"' , '"+str(session.get('DelPh'))+"', '" +str(session.get('RecName'))+"','"+str(session.get('DOR'))+"','"+str(session.get('RecPh'))+"','"+str(session.get('otp'))+"');"
		print(query)
		try:
			cursor.execute(query)
			mysql.connection.commit()
			cursor.close()
			return render_template('/OTPsuccess.html')
		except:
			return render_template('/OTPerror.html')
	else:
		return render_template('/OTPerror.html')
@app.route('/adminLogin')
def adminHome():
	if not session.get('AdminLoggedIn'):
		return render_template('AdminLogin.html')
	else:
		return render_template('adminHome.html')
@app.route('/admincheck', methods = ['POST'])
def adminLogIn():
	h = hashlib.md5(request.form['password'].encode())
	hpwd = h.hexdigest()
	cursor = mysql.connection.cursor()
	query = "SELECT Password FROM admin WHERE UserName='"+request.form['username']+"';"
	cursor.execute(query)
	print(query)
	if cursor.rowcount !=0:
		for row in cursor.fetchone():
			password = row
			print(password)	
		if hpwd == password:
			session['AdminLoggedIn'] = True
			return render_template('adminHome.html')
		else:
			return render_template("/loginError.html")
	else:
		return render_template("/loginError.html")
	cursor.close()
@app.route('/downloadcsv',methods = ['POST'])
def download_csv():
	fromdate = request.form['fromdate']
	todate = request.form['todate']
	print(fromdate)
	print(todate)
	if fromdate == "" and todate != "":
		query = "select * from sales WHERE (DOR<'"+todate+"');"
		Dfilename = "sales_acknowledgement_data_from begining to"+todate+".csv"
	if fromdate != "" and todate == "":
		query = "select * from sales WHERE (DOR>'"+fromdate+"');"
		Dfilename = "sales_acknowledgement_data_from"+fromdate+"till end.csv"
	if fromdate == "" and todate == "":
		query = "select * from sales"
		Dfilename = "sales_acknowledgement_data_FULL"
	if fromdate != "" and todate != "":
		query = "select * from sales where (DOI >'"+fromdate+"' and DOI < '"+todate+"');"
		Dfilename = "sales_acknowledgement_data_from"+fromdate+"to"+todate+".csv"
	cursor = mysql.connection.cursor()
	cursor.execute(query)
	data = pd.DataFrame(cursor.fetchall(),columns = ['InvoiceNbr','Invoice Date','Delivery Phone Number','Reciever Name','Date of Delivery','Reciver Phone Number','OTP'])
	filename = "C:/Users/Mohit Arora/Documents/work/Projects/Sales_Acknowledgement/created_files/sales_acknowledgement_data_from"+fromdate+"to"+todate+".csv"
	data.to_csv(filename)
	with open(filename) as fp:
		csv = fp.read()

	return Response(csv,mimetype="text/csv",headers={"Content-disposition":"attachment; filename="+filename})
@app.route('/logout')
def do_logout():
	if not session.get('AdminLoggedIn'):
		if not session.get('logged_in') :
			return render_template('loginSelector.html')
		else:
			session['logged_in'] = False
			session.clear()
			return home()
			pass
	else:
		session['AdminLoggedIn'] = False
		session.clear()
		return home()
if __name__ == '__main__':
    waitress.serve(app,host='0.0.0.0',port='8080')