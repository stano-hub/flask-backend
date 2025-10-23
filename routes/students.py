from flask import Blueprint, request, jsonify
from utils.db import connection_pool

student_bp = Blueprint("student_bp", __name__)

# ===========================
# ➕ Add a Student
# ===========================
@student_bp.route("/api/students", methods=["POST"])
def add_student():
    try:
        data = request.get_json()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        age = data.get("age")
        parent_contact = data.get("parent_contact")
        class_id = data.get("class_id")

        if not all([first_name, last_name, class_id]):
            return jsonify({"error": "Missing required fields"}), 400

        conn = connection_pool.getconn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO students (first_name, last_name, age, parent_contact, class_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (first_name, last_name, age, parent_contact, class_id),
        )
        conn.commit()

        cur.close()
        connection_pool.putconn(conn)

        return jsonify({"message": "Student added successfully"}), 201

    except Exception as e:
        print("Error adding student:", str(e))
        return jsonify({"error": "Failed to add student"}), 500


# ===========================
# 📋 Get All Students
# ===========================
@student_bp.route("/api/students", methods=["GET"])
def get_students():
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            SELECT s.id, s.first_name, s.last_name, s.age, s.parent_contact, 
                   c.class_name, c.subclass
            FROM students s
            JOIN classes c ON s.class_id = c.id
            ORDER BY c.class_name, c.subclass, s.last_name
        """)
        students = cur.fetchall()

        cur.close()
        connection_pool.putconn(conn)

        result = [
            {
                "id": s[0],
                "first_name": s[1],
                "last_name": s[2],
                "age": s[3],
                "parent_contact": s[4],
                "class_name": s[5],
                "subclass": s[6],
            }
            for s in students
        ]

        return jsonify(result), 200

    except Exception as e:
        print("Error fetching students:", str(e))
        return jsonify({"error": "Failed to fetch students"}), 500


# ===========================
# 🎯 Get Students by Class ID
# ===========================
@student_bp.route("/api/students/<int:class_id>", methods=["GET"])
def get_students_by_class(class_id):
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            SELECT s.id, s.first_name, s.last_name, s.age, s.parent_contact,
                   c.class_name, c.subclass
            FROM students s
            JOIN classes c ON s.class_id = c.id
            WHERE s.class_id = %s
            ORDER BY s.last_name
        """, (class_id,))
        students = cur.fetchall()

        cur.close()
        connection_pool.putconn(conn)

        result = [
            {
                "id": s[0],
                "first_name": s[1],
                "last_name": s[2],
                "age": s[3],
                "parent_contact": s[4],
                "class_name": s[5],
                "subclass": s[6],
            }
            for s in students
        ]

        return jsonify(result), 200

    except Exception as e:
        print("Error fetching students by class:", str(e))
        return jsonify({"error": "Failed to fetch students for this class"}), 500
