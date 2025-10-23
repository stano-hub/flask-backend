from flask import Blueprint, request, jsonify
from utils.db import connection_pool

class_bp = Blueprint("class_bp", __name__)

# ===========================
# ➕ Add a Class/Subclass
# ===========================
@class_bp.route("/api/classes", methods=["POST"])
def add_class():
    try:
        data = request.get_json()
        class_name = data.get("class_name")
        subclass = data.get("subclass")

        if not class_name:
            return jsonify({"error": "class_name is required"}), 400

        conn = connection_pool.getconn()
        cur = conn.cursor()

        # Ensure subclass is optional
        if subclass:
            cur.execute(
                "SELECT id FROM classes WHERE class_name = %s AND subclass = %s",
                (class_name, subclass),
            )
        else:
            cur.execute(
                "SELECT id FROM classes WHERE class_name = %s AND subclass IS NULL",
                (class_name,),
            )

        if cur.fetchone():
            cur.close()
            connection_pool.putconn(conn)
            return jsonify({"error": "Class or subclass already exists"}), 400

        cur.execute(
            "INSERT INTO classes (class_name, subclass) VALUES (%s, %s)",
            (class_name, subclass),
        )
        conn.commit()

        cur.close()
        connection_pool.putconn(conn)

        return jsonify({"message": "Class created successfully"}), 201

    except Exception as e:
        print("Error adding class:", str(e))
        return jsonify({"error": "Failed to add class"}), 500


# ===========================
# 📋 Get All Classes
# ===========================
@class_bp.route("/api/classes", methods=["GET"])
def get_classes():
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()

        cur.execute("SELECT id, class_name, subclass FROM classes ORDER BY class_name, subclass")
        classes = cur.fetchall()

        cur.close()
        connection_pool.putconn(conn)

        result = [
            {"id": c[0], "class_name": c[1], "subclass": c[2]} for c in classes
        ]

        return jsonify(result), 200

    except Exception as e:
        print("Error fetching classes:", str(e))
        return jsonify({"error": "Failed to fetch classes"}), 500
