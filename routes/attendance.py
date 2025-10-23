from flask import Blueprint, request, jsonify
from utils.db import connection_pool
from datetime import date

attendance_bp = Blueprint("attendance_bp", __name__)

# ===========================
# 🧾 Mark Attendance (Bulk)
# ===========================
@attendance_bp.route("/api/attendance", methods=["POST"])
def mark_attendance():
    try:
        data = request.get_json()
        class_id = data.get("class_id")
        marked_by = data.get("marked_by")
        attendance_list = data.get("attendance_list")  # list of {student_id, status}

        if not all([class_id, marked_by, attendance_list]):
            return jsonify({"error": "Missing required fields"}), 400

        conn = connection_pool.getconn()
        cur = conn.cursor()

        # Check if attendance for this class and date already exists
        cur.execute("""
            SELECT DISTINCT class_id FROM attendance
            WHERE class_id = %s AND date = %s
        """, (class_id, date.today()))
        if cur.fetchone():
            cur.close()
            connection_pool.putconn(conn)
            return jsonify({"error": "Attendance already marked for this class today"}), 400

        # Bulk insert attendance records
        for record in attendance_list:
            student_id = record.get("student_id")
            status = record.get("status", "absent")
            cur.execute("""
                INSERT INTO attendance (student_id, class_id, date, status, marked_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (student_id, class_id, date.today(), status, marked_by))

        conn.commit()
        cur.close()
        connection_pool.putconn(conn)

        return jsonify({"message": "Attendance marked successfully"}), 201

    except Exception as e:
        print("Error marking attendance:", str(e))
        return jsonify({"error": "Failed to mark attendance"}), 500


# ===========================
# 📅 Get Attendance by Date/Class
# ===========================
@attendance_bp.route("/api/attendance", methods=["GET"])
def get_attendance():
    try:
        class_id = request.args.get("class_id")
        selected_date = request.args.get("date", str(date.today()))

        if not class_id:
            return jsonify({"error": "class_id is required"}), 400

        conn = connection_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            SELECT a.id, s.first_name, s.last_name, a.status, a.date, t.name AS marked_by
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            JOIN teachers t ON a.marked_by = t.id
            WHERE a.class_id = %s AND a.date = %s
            ORDER BY s.last_name
        """, (class_id, selected_date))
        records = cur.fetchall()

        cur.close()
        connection_pool.putconn(conn)

        result = [
            {
                "attendance_id": r[0],
                "first_name": r[1],
                "last_name": r[2],
                "status": r[3],
                "date": r[4],
                "marked_by": r[5]
            }
            for r in records
        ]

        return jsonify(result), 200

    except Exception as e:
        print("Error fetching attendance:", str(e))
        return jsonify({"error": "Failed to fetch attendance"}), 500


# ===========================
# ✏️ Update Attendance (Same Day)
# ===========================
@attendance_bp.route("/api/attendance/<int:attendance_id>", methods=["PUT"])
def update_attendance(attendance_id):
    try:
        data = request.get_json()
        new_status = data.get("status")

        if new_status not in ["present", "absent"]:
            return jsonify({"error": "Invalid status"}), 400

        conn = connection_pool.getconn()
        cur = conn.cursor()

        # Only allow updates for today's records
        cur.execute("""
            UPDATE attendance
            SET status = %s
            WHERE id = %s AND date = %s
            RETURNING id
        """, (new_status, attendance_id, date.today()))

        updated = cur.fetchone()
        conn.commit()
        cur.close()
        connection_pool.putconn(conn)

        if not updated:
            return jsonify({"error": "Cannot edit past attendance or invalid record"}), 400

        return jsonify({"message": "Attendance updated successfully"}), 200

    except Exception as e:
        print("Error updating attendance:", str(e))
        return jsonify({"error": "Failed to update attendance"}), 500
