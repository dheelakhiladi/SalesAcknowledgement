import requests
import hashlib
def sendOTP(otp,tonumber):

	url = "https://www.fast2sms.com/dev/bulk"
	querystring = {"authorization":"BJxZ9aKWsoghHG7ATUYyf5P86qm14tOVIRQzdp3lwMjDcEnXrvVDsGi80lLTh2ug4tJqAn1aSIX7xPR9","sender_id":"FSTSMS","message":"Your OTP is"+otp+" for D.N. Agencies order Acknowledgement ","language":"english","route":"p","numbers":tonumber}
	headers = {
    	'cache-control': "no-cache"
	}
	response = requests.request("GET", url, headers=headers, params=querystring)
	print(response.text)
	pass
	#Himanshu Password = DevkiNandan0989
def pass_hash():
	user_entered_password = 'Sonyvaio'
	actual_password = "Sonyvaio"
	db_password = user_entered_password
	h = hashlib.md5(db_password.encode())
	h1 = hashlib.md5(actual_password.encode())
	print(h.hexdigest())
	print(h1.hexdigest())
pass_hash()
