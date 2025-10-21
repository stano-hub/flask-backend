from flask import *
import pymysql.cursors
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
import pymysql
import pymysql.cursors

app.config['UPLOAD_FOLDER'] = 'mysite/static/images'

@app.route('/api/signup' , methods=['POST'])
def signup():
    # receive data which has been send to server in the request
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']

    connection = pymysql.connect(host='Jacecarrison.mysql.pythonanywhere-services.com' , user='Jacecarrison' , password='Modcom25' , database='Jacecarrison$default')

    cursor = connection.cursor()
    sql ='insert into users(username,email ,password,phone ) values(%s,%s,%s,%s)'

    data = (username, email, password, phone)

    cursor.execute(sql, data)
    connection.commit()


    return jsonify({"success": "Thank you for joning"})

@app.route('/api/signin' , methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    connection = pymysql.connect(host='Jacecarrison.mysql.pythonanywhere-services.com' , user='Jacecarrison' , password='Modcom25' , database='Jacecarrison$default')

    cursor =  connection.cursor(pymysql.cursors.DictCursor)
    sql= 'select * from users where email  = %s and password=%s'
    data=(email,password)
    cursor.execute(sql, data)

    count = cursor.rowcount

    if count == 0:
        return jsonify({"message" : data})
    else:
        user = cursor.fetchone()
        return jsonify({"message" : "login successful" , "user":user})


@app.route('/api/add_product', methods=['POST'])
def add_product():
    product_name = request.form['product_name']
    product_description = request.form['product_description']
    product_cost = request.form['product_cost']
    photo = request.files['product_photo']

    filename = photo.filename

    photo_path= os.path.join(app.config['UPLOAD_FOLDER'], filename)
    photo.save(photo_path)

    # connect to db
    connection = pymysql.connect(host='Jacecarrison.mysql.pythonanywhere-services.com', user='Jacecarrison',password='Modcom25', database='Jacecarrison$default')
    cursor = connection.cursor()

    sql = 'insert into product_details(product_name, product_description, product_cost, product_photo) values (%s,%s,%s,%s)'
    data= (product_name, product_description, product_cost, filename)
    cursor.execute(sql, data)
    connection.commit()
    return jsonify({"success": "product details added successfully"})

@app.route('/api/get_product_details' , methods=['GET'])
def get_product_details():
    connection = pymysql.connect(host='Jacecarrison.mysql.pythonanywhere-services.com' , user='Jacecarrison' , password='Modcom25', database='Jacecarrison$default')
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql='select * from product_details'

    cursor.execute(sql)

    product_details = cursor. fetchall()
    return jsonify(product_details)

    # Mpesa Payment Route

import requests
from requests.auth import HTTPBasicAuth
import datetime
import base64


@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        # Extract POST Values sent
        amount = request.form['amount']
        phone = request.form['phone']

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        # Provide your consumer_key and consumer_secret
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Get response as Dictionary
        data = response.json()
        # Retrieve the Provide Token
        # Token allows you to proceed with the transaction
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
        business_short_code = "174379"  # Test Paybile (Safaricom Provided)
        # Combine above 3 Strings to get data variable
        data = business_short_code + passkey + timestamp
        # Encode to Base64
        encoded = base64.b64encode(data.encode())
        password = encoded.decode()

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password":password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": "1",  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://coding.co.ke/api/confirm.php",
            "AccountReference": "SokoGarden Online",
            "TransactionDesc": "Payments for Products"
        }

        # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        # Specify STK Push  Trigger URL
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        # Create a POST Request to above url, providing headers, payload
        # Below triggers an STK Push to the phone number indicated in the payload and the amount.
        response = requests.post(url, json=payload, headers=headers)
        print(response.text) #
        # Give a Response
        return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})
# app.run(debug=True)
