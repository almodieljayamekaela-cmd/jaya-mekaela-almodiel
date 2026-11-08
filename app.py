
import os
import sqlite3
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "students.db")

PARTNER_API_URL = "https://maryjoydebaja.onrender.com/api/students"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year INTEGER NOT NULL,
            section TEXT NOT NULL,
            source TEXT DEFAULT 'Local'
        )
    """)

    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(students)").fetchall()
    ]

    if "source" not in columns:
        conn.execute(
            "ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'"
        )

    conn.commit()
    conn.close()


@app.before_request
def prepare_database():
    init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/hello")
def hello():
    return jsonify({"message": "Hello from Jaya's Flask API!"})


@app.route("/student")
def student():
    return jsonify({
        "student_id": "24-00328",
        "name": "Jaya Mekaela Almodiel",
        "program": "BSIT",
        "year": "3rd Year",
        "section": "HAMILTON"
    })


@app.route("/course")
def course():
    return jsonify({
        "course_code": "IT3120",
        "course_title": "System Integration",
        "instructor": "Dr. Rene Arduo",
        "semester": "1st Semester",
        "academic_year": "2026-2027"
    })


@app.route("/greet")
def greet():
    name = request.args.get("name", "Student")
    return jsonify({"message": f"Hello, {name}!"})


@app.route("/profile")
def profile():
    return jsonify({
        "student_id": "24-00328",
        "name": "Jaya Mekaela Almodiel",
        "program": "BSIT",
        "year": 3,
        "section": "HAMILTON"
    })


@app.route("/students", methods=["GET"])
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_db()
    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route("/students", methods=["POST"])
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No student data received"}), 400

    required = ["student_id", "name", "program", "year", "section"]

    if not all(data.get(field) not in (None, "") for field in required):
        return jsonify({"error": "Please provide all required fields"}), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400

    source = data.get("source", "Local")

    try:
        conn = get_db()

        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            year,
            data["section"],
            source
        ))

        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "message": "Student added successfully",
            "id": new_id
        }), 201

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500


@app.route("/students/search/<student_id>")
def search_student(student_id):
    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No student data received"}), 400

    required = ["student_id", "name", "program", "year", "section"]

    if not all(data.get(field) not in (None, "") for field in required):
        return jsonify({"error": "Please provide all required fields"}), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400

    conn = get_db()

    existing = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    if existing is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    conn.execute("""
        UPDATE students
        SET student_id = ?, name = ?, program = ?,
            year = ?, section = ?
        WHERE id = ?
    """, (
        data["student_id"],
        data["name"],
        data["program"],
        year,
        data["section"],
        id
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Student updated successfully"})


@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db()

    existing = conn.execute(
        "SELECT id FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    if existing is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Student deleted successfully"})


@app.route("/students/program/<program>")
def students_by_program(program):
    conn = get_db()

    students = conn.execute(
        "SELECT * FROM students WHERE program = ?",
        (program,)
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


@app.route("/partner-records", methods=["GET"])
def partner_records():
    try:
        response = requests.get(PARTNER_API_URL, timeout=15)
        response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            return jsonify({"error": "Partner API did not return a list"}), 502

        return jsonify(records)

    except requests.RequestException as error:
        return jsonify({
            "error": "Unable to retrieve partner data",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({"error": "Partner API returned invalid JSON"}), 502


@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No student data received"}), 400

    required = ["student_id", "name", "program", "year", "section"]

    if not all(data.get(field) not in (None, "") for field in required):
        return jsonify({"error": "Missing required student information"}), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400

    try:
        conn = get_db()

        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            year,
            data["section"],
            "Classmate API"
        ))

        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "message": "Remote record saved",
            "id": new_id
        }), 201

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500


@app.route("/classmate-students")
def classmate_students():
    return partner_records()


@app.route("/grades/<student_id>")
def grades(student_id):
    return jsonify({
        "student_id": student_id,
        "grades": [
            {"course": "System Integration", "grade": 1.50},
            {"course": "Advanced Database Systems", "grade": 1.75},
            {"course": "Artificial Intelligence", "grade": 1.50}
        ]
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
