from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Import routes
from routes.teachers import teachers_bp
from routes.classes import classes_bp
from routes.students import students_bp
from routes.attendance import attendance_bp
from routes.analytics import analytics_bp

# Load environment variables
load_dotenv()

# ==========================
# ⚙️ Flask App Configuration
# ==========================
app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_jwt_secret_key_here")

# ==========================
# 🔗 Register Blueprints
# ==========================
app.register_blueprint(teachers_bp)
app.register_blueprint(classes_bp)
app.register_blueprint(students_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(analytics_bp)

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
