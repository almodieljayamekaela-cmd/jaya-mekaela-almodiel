import os
import sqlite3
import requests

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "students.db")

PARTNER_URL = "https://maryjoydebaja.onrender.com"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            program TEXT,
            year INTEGER,
            section TEXT,
            source TEXT DEFAULT 'Local'
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_code TEXT,
            course_title TEXT,
            grade TEXT
        )
    """)

    connection.commit()
    connection.close()


def student_to_dict(student):
    return dict(student)


initialize_database()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/student")
def student():
    return jsonify({
        "student_id": "24-00328",
        "name": "Jaya Mekaela Almodiel",
        "program": "BSIT",
        "year": 3,
        "section": "HAMILTON"
    })


@app.route("/hello")
def hello():
    return jsonify({"message": "Hello from Jaya's Flask API!"})


@app.route("/course")
def course():
    return jsonify({
        "course_code": "IT3120",
        "course_title": "System Integration",
        "instructor": "Dr. Rene Arduo"
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
        "section": "HAMILTON",
        "course": "IT3120 - System Integration"
    })


@app.route("/api/students", methods=["GET"])
def get_students():
    connection = get_db_connection()
    students = connection.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return jsonify([student_to_dict(s) for s in students])


@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No student data received"}), 400

    required_fields = ["student_id", "name"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    connection = get_db_connection()

    try:
        connection.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get("student_id"),
            data.get("name"),
            data.get("program", ""),
            data.get("year", ""),
            data.get("section", ""),
            data.get("source", "Local")
        ))

        connection.commit()

        return jsonify({
            "message": "Student added successfully!",
            "student": data
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 409

    finally:
        connection.close()


@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No update data received"}), 400

    connection = get_db_connection()

    existing = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if not existing:
        connection.close()
        return jsonify({"error": "Student not found"}), 404

    try:
        connection.execute("""
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
        """, (
            data.get("student_id", existing["student_id"]),
            data.get("name", existing["name"]),
            data.get("program", existing["program"]),
            data.get("year", existing["year"]),
            data.get("section", existing["section"]),
            student_id
        ))

        connection.commit()

        return jsonify({"message": "Student updated successfully!"})

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 409

    finally:
        connection.close()


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    connection = get_db_connection()

    result = connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    if result.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully!"})


@app.route("/students/search/<student_id>", methods=["GET"])
def search_student(student_id):
    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    ).fetchone()

    connection.close()

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student_to_dict(student))


@app.route("/partner-records", methods=["GET"])
def get_partner_records():
    try:
        response = requests.get(
            f"{PARTNER_URL}/api/students",
            timeout=30
        )

        response.raise_for_status()

        records = response.json()

        if isinstance(records, dict):
            records = records.get("students", records.get("data", []))

        if not isinstance(records, list):
            return jsonify({
                "error": "Partner API did not return a list of student records"
            }), 502

        return jsonify(records)

    except requests.RequestException as error:
        return jsonify({
            "error": "Unable to retrieve records from partner API",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({
            "error": "Partner API returned an invalid response"
        }), 502


@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No student record received"}), 400

    if not data.get("student_id") or not data.get("name"):
        return jsonify({
            "error": "Student ID and name are required"
        }), 400

    connection = get_db_connection()

    try:
        connection.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get("student_id"),
            data.get("name"),
            data.get("program", ""),
            data.get("year", ""),
            data.get("section", ""),
            "Classmate API"
        ))

        connection.commit()

        return jsonify({
            "message": "Partner student record imported successfully!"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "This student record already exists in your database"
        }), 409

    finally:
        connection.close()


@app.route("/send-to-partner", methods=["POST"])
def send_to_partner():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No record received"}), 400

    try:
        response = requests.post(
            f"{PARTNER_URL}/api/students",
            json=data,
            timeout=30
        )

        try:
            partner_response = response.json()
        except ValueError:
            partner_response = response.text

        if not response.ok:
            return jsonify({
                "error": "Partner API rejected the record",
                "partner_status": response.status_code,
                "partner_response": partner_response
            }), 502

        return jsonify({
            "message": "Record successfully sent to partner!",
            "partner_response": partner_response
        }), 200

    except requests.RequestException as error:
        return jsonify({
            "error": "Unable to send record to partner",
            "details": str(error)
        }), 502


@app.route("/grades/<student_id>", methods=["GET"])
def get_grades(student_id):
    connection = get_db_connection()

    grades = connection.execute(
        "SELECT * FROM grades WHERE student_id = ?",
        (student_id,)
    ).fetchall()

    connection.close()

    return jsonify([dict(grade) for grade in grades])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))