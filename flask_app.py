from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================
# ⚙️ Flask App Configuration
# ==========================
app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_jwt_secret_key_here")

# ==========================
# 🔗 Import and Register Blueprints
# ==========================
from routes.teachers import teacher_bp
from routes.classes import class_bp
from routes.students import student_bp
from routes.attendance import attendance_bp
from routes.analytics import analytics_bp

app.register_blueprint(teacher_bp, url_prefix="/teachers")
app.register_blueprint(class_bp, url_prefix="/classes")
app.register_blueprint(student_bp, url_prefix="/students")
app.register_blueprint(attendance_bp, url_prefix="/attendance")
app.register_blueprint(analytics_bp, url_prefix="/analytics")

# ==========================
# 🏠 Root Endpoint
# ==========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "✅ VBS Attendance System Backend Running Successfully",
        "status": "online"
    }), 200

# ==========================
# 🚀 Run App
# ==========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
