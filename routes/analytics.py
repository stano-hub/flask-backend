from flask import Blueprint, jsonify, request
from utils.db import connection_pool

analytics_bp = Blueprint("analytics_bp", __name__)

# ===========================
# 📊 Get General Summary
# ===========================
@analytics_bp.route("/api/analytics/summary", methods=["GET"])
def get_summary():
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()

        # Total students
        cur.execute("SELECT COUNT(*) FROM students")
        total_students = cur.fetchone()[0]

        # Total classes
        cur.execute("SELECT COUNT(*) FROM classes")
        total_classes = cur.fetchone()[0]

        # Total teachers
        cur.execute("SELECT COUNT(*) FROM teachers WHERE role = 'teacher'")
        total_teachers = cur.fetchone()[0]

        # Total attendance entries
        cur.execute("SELECT COUNT(*) FROM attendance")
        total_records = cur.fetchone()[0]

        cur.close()
        connection_pool.putconn(conn)

        return jsonify({
            "total_students": total_students,
            "total_classes": total_classes,
            "total_teachers": total_teachers,
            "total_attendance_records": total_records
        }), 200

    except Exception as e:
        print("Error fetching analytics summary:", str(e))
        return jsonify({"error": "Failed to fetch summary"}), 500


# ===========================
# 📅 Attendance by Date (Trend)
# ===========================
@analytics_bp.route("/api/analytics/daily", methods=["GET"])
def get_attendance_by_date():
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            SELECT date, COUNT(*) FILTER (WHERE status = 'present') AS present_count,
                   COUNT(*) FILTER (WHERE status = 'absent') AS absent_count
            FROM attendance
            GROUP BY date
            ORDER BY date ASC
        """)
        rows = cur.fetchall()

        cur.close()
        connection_pool.putconn(conn)

        trend_data = [
            {
                "date": str(r[0]),
                "present_count": r[1],
                "absent_count": r[2],
                "total": r[1] + r[2]
            }
            for r in rows
        ]

        return jsonify(trend_data), 200

    except Exception as e:
        print("Error fetching attendance trend:", str(e))
        return jsonify({"error": "Failed to fetch attendance trend"}), 500


# ===========================
# 🏫 Attendance by Class
# ===========================
@analytics_bp.route("/api/analytics/classes", methods=["GET"])
def get_class_analytics():
    try:
        conn = connection_pool.getconn()
        cur = conn.cursor()

        cur.execute("""
            SELECT c.class_name, c.subclass,
                   COUNT(a.id) FILTER (WHERE a.status = 'present') AS present_count,
                   COUNT(a.id) FILTER (WHERE a.status = 'absent') AS absent_count
            FROM classes c
            LEFT JOIN attendance a ON a.class_id = c.id
            GROUP BY c.class_name, c.subclass
            ORDER BY c.class_name, c.subclass
        """)
        rows = cur.fetchall()

        cur.close()
        connection_pool.putconn(conn)

        result = [
            {
                "class_name": r[0],
                "subclass": r[1],
                "present": r[2],
                "absent": r[3],
                "total": (r[2] or 0) + (r[3] or 0)
            }
            for r in rows
        ]

        return jsonify(result), 200

    except Exception as e:
        print("Error fetching class analytics:", str(e))
        return jsonify({"error": "Failed to fetch class analytics"}), 500
