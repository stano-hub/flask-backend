from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
import os
from utils.db import connection_pool

teacher_bp = Blueprint("teacher_bp", __name__)

# Retrieve secret key directly from Render environment
SECRET_KEY = os.environ["SECRET_KEY"]

# ===========================
# 🧩 Teacher Signup
# ===========================
@teacher_bp.route("/api/teachers/signup", methods=["POST"])
def signup_teacher():
    try:
        data = request.get_json()
        name = data.get("name")
        phone = data.get("phone")
        password = data.get("password")
        role = data.get("role", "teacher")

        if not all([name, phone, password]):
            return jsonify({"error": "Missing required fields"}), 400

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        conn = connection_pool.getconn()
        cur = conn.cursor()

        # Check if the phone number already exists
        cur.execute("SELECT id FROM teachers WHERE phone = %s", (phone,))
        if cur.fetchone():
            cur.close()
            connection_pool.putconn(conn)
            return jsonify({"error": "Phone number already registered"}), 400

        # Insert the new teacher
        cur.execute(
            "INSERT INTO teachers (name, phone, password, role) VALUES (%s, %s, %s, %s)",
            (name, phone, hashed_password.decode("utf-8"), role),
        )
        conn.commit()

        cur.close()
        connection_pool.putconn(conn)

        return jsonify({"message": "Teacher registered successfully"}), 201

    except Exception as e:
        print("Error during signup:", str(e))
        return jsonify({"error": "Signup failed"}), 500


# ===========================
# 🔐 Teacher Signin
# ===========================
@teacher_bp.route("/api/teachers/signin", methods=["POST"])
def signin_teacher():
    try:
        data = request.get_json()
        phone = data.get("phone")
        password = data.get("password")

        if not all([phone, password]):
            return jsonify({"error": "Missing required fields"}), 400

        conn = connection_pool.getconn()
        cur = conn.cursor()

        cur.execute("SELECT id, name, phone, password, role FROM teachers WHERE phone = %s", (phone,))
        teacher = cur.fetchone()

        cur.close()
        connection_pool.putconn(conn)

        if not teacher:
            return jsonify({"error": "Invalid phone or password"}), 401

        teacher_id, name, phone, hashed_password, role = teacher

        # Verify password
        if not bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            return jsonify({"error": "Invalid phone or password"}), 401

        # Generate JWT token (expires in 8 hours)
        token = jwt.encode(
            {
                "teacher_id": teacher_id,
                "role": role,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8),
            },
            SECRET_KEY,
            algorithm="HS256",
        )

        return jsonify({
            "message": "Login successful",
            "token": token,
            "teacher": {
                "id": teacher_id,
                "name": name,
                "phone": phone,
                "role": role
            }
        }), 200

    except Exception as e:
        print("Error during signin:", str(e))
        return jsonify({"error": "Signin failed"}), 500
