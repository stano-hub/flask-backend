from flask import Flask, request, jsonify
import pymysql
import pymysql.cursors
from flask_cors import CORS
import os
import requests
from requests.auth import HTTPBasicAuth
import datetime
import base64

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'mysite/static/images')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ======================== SIGNUP ROUTE ========================
@app.route('/api/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    phone = request.form['phone']

    connection = pymysql.connect(
        host='Jacecarrison.mysql.pythonanywhere-services.com',
        user='Jacecarrison',
        password='Modcom25',
        database='Jacecarrison$default'
    )

    cursor = connection.cursor()
    sql = 'INSERT INTO users(username, email, password, phone) VALUES (%s, %s, %s, %s)'
    data = (username, email, password, phone)
    cursor.execute(sql, data)
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"success": "Thank you for joining!"})


# ======================== SIGNIN ROUTE ========================
@app.route('/api/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    connection = pymysql.connect(
        host='Jacecarrison.mysql.pythonanywhere-services.com',
        user='Jacecarrison',
        password='Modcom25',
        database='Jacecarrison$default'
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT * FROM users WHERE email = %s AND password = %s'
    cursor.execute(sql, (email, password))

    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        return jsonify({"message": "login successful", "user": user})
    else:
        return jsonify({"message": "Invalid email or password"}), 401


# ======================== ADD PRODUCT ROUTE ========================
@app.route('/api/add_product', methods=['POST'])
def add_product():
    product_name = request.form['product_name']
    product_description = request.form['product_description']
    product_cost = request.form['product_cost']
    photo = request.files['product_photo']

    filename = photo.filename
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    photo.save(photo_path)

    connection = pymysql.connect(
        host='Jacecarrison.mysql.pythonanywhere-services.com',
        user='Jacecarrison',
        password='Modcom25',
        database='Jacecarrison$default'
    )

    cursor = connection.cursor()
    sql = 'INSERT INTO product_details(product_name, product_description, product_cost, product_photo) VALUES (%s, %s, %s, %s)'
    cursor.execute(sql, (product_name, product_description, product_cost, filename))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"success": "Product details added successfully"})


# ======================== GET PRODUCTS ROUTE ========================
@app.route('/api/get_product_details', methods=['GET'])
def get_product_details():
    connection = pymysql.connect(
        host='Jacecarrison.mysql.pythonanywhere-services.com',
        user='Jacecarrison',
        password='Modcom25',
        database='Jacecarrison$default'
    )

    cursor = connection.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT * FROM product_details'
    cursor.execute(sql)

    product_details = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(product_details)


# ======================== MPESA PAYMENT ROUTE ========================
@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    amount = request.form['amount']
    phone = request.form['phone']

    consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
    consumer_secret = "amFbAoUByPV2rM5A"

    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = response.json()
    access_token = "Bearer " + data['access_token']

    timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    business_short_code = "174379"
    combined_data = business_short_code + passkey + timestamp
    password = base64.b64encode(combined_data.encode()).decode()

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": business_short_code,
        "PhoneNumber": phone,
        "CallBackURL": "https://coding.co.ke/api/confirm.php",
        "AccountReference": "SokoGarden Online",
        "TransactionDesc": "Payments for Products"
    }

    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(url, json=payload, headers=headers)

    return jsonify({"message": "An MPESA Prompt has been sent to your phone, please check & complete payment"})


# ======================== MAIN ========================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=False)
