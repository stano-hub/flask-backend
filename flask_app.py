from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
import psycopg2.extras
import requests
from requests.auth import HTTPBasicAuth
import datetime
import base64
import urllib.parse as up

# ==============================
# Flask App Setup
# ==============================
app = Flask(__name__)
CORS(app)

# ==============================
# Database Connection Setup
# ==============================
up.uses_netloc.append("postgres")
url = up.urlparse(os.environ.get("DATABASE_URL"))

# Create ONE global connection (Render auto-restores on restart)
def get_db_connection():
    return psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

# Create connection once
connection = get_db_connection()
connection.autocommit = True


# ==============================
# API ROUTES
# ==============================

# ---------- SIGNUP ----------
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.form or request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, email, password, phone) VALUES (%s, %s, %s, %s)",
                (username, email, password, phone)
            )
        return jsonify({"success": "Thank you for joining!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- SIGNIN ----------
@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.form or request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s",
                (email, password)
            )
            user = cursor.fetchone()

        if not user:
            return jsonify({"message": "Invalid email or password"}), 401

        return jsonify({"message": "Login successful", "user": user})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- ADD PRODUCT ----------
@app.route('/api/add_product', methods=['POST'])
def add_product():
    try:
        product_name = request.form['product_name']
        product_description = request.form['product_description']
        product_cost = request.form['product_cost']
        photo = request.files['product_photo']

        upload_folder = os.path.join(os.getcwd(), 'static', 'images')
        os.makedirs(upload_folder, exist_ok=True)

        filename = photo.filename
        photo_path = os.path.join(upload_folder, filename)
        photo.save(photo_path)

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO product_details (product_name, product_description, product_cost, product_photo) VALUES (%s, %s, %s, %s)",
                (product_name, product_description, product_cost, filename)
            )

        return jsonify({"success": "Product details added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- GET PRODUCTS ----------
@app.route('/api/get_product_details', methods=['GET'])
def get_product_details():
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM product_details ORDER BY id DESC")
            products = cursor.fetchall()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- MPESA PAYMENT ----------
@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    try:
        amount = request.form['amount']
        phone = request.form['phone']

        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Step 1: Get Access Token
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        access_token = "Bearer " + response.json()['access_token']

        # Step 2: Prepare STK Push
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        business_short_code = "174379"
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

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

        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        stk_response = requests.post(stk_url, json=payload, headers=headers)

        return jsonify({"message": "An MPESA Prompt has been sent to your phone", "safaricom_response": stk_response.json()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- HEALTH CHECK ----------
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Server running successfully ✅"})


# ==============================
# Run the App (Render compatible)
# ==============================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
