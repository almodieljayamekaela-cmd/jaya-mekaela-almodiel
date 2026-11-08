
import os
import sqlite3
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.db")
PARTNER_URL = "https://maryjoydebaja.onrender.com"


def get_db_connection():
    connection = sqlite3.connect(DATABASE, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            program TEXT DEFAULT '',
            year INTEGER DEFAULT 0,
            section TEXT DEFAULT '',
            source TEXT DEFAULT 'Local'
        )
    """)

    columns = {
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(students)"
        ).fetchall()
    }

    migrations = {
        "student_id": "TEXT DEFAULT ''",
        "name": "TEXT DEFAULT ''",
        "program": "TEXT DEFAULT ''",
        "year": "INTEGER DEFAULT 0",
        "section": "TEXT DEFAULT ''",
        "source": "TEXT DEFAULT 'Local'"
    }

    for column, definition in migrations.items():
        if column not in columns:
            connection.execute(
                f"ALTER TABLE students ADD COLUMN {column} {definition}"
            )

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


initialize_database()


def prepare_student(data):
    return {
        "student_id": str(data.get("student_id", "")).strip(),
        "name": str(data.get("name", "")).strip(),
        "program": str(data.get("program", "")).strip(),
        "year": int(data.get("year") or 0),
        "section": str(data.get("section", "")).strip()
    }


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
    return jsonify({
        "message": f"Hello, {request.args.get('name', 'Student')}!"
    })


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


# ADD STUDENT AND SHOW ALL RECORDS

@app.route("/api/students", methods=["GET"])
def get_students():
    try:
        with get_db_connection() as connection:
            students = connection.execute(
                "SELECT * FROM students ORDER BY id DESC"
            ).fetchall()

        return jsonify([dict(student) for student in students])

    except sqlite3.Error as error:
        app.logger.exception("Get students error")
        return jsonify({"error": str(error)}), 500


@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No student data received"}), 400

    try:
        student = prepare_student(data)

        if not student["student_id"] or not student["name"]:
            return jsonify({
                "error": "Student ID and name are required"
            }), 400

        with get_db_connection() as connection:
            connection.execute("""
                INSERT INTO students
                (student_id, name, program, year, section, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                student["student_id"],
                student["name"],
                student["program"],
                student["year"],
                student["section"],
                "Local"
            ))

        return jsonify({
            "message": "Student added successfully!"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 409

    except (sqlite3.Error, ValueError, TypeError) as error:
        app.logger.exception("Add student error")
        return jsonify({"error": str(error)}), 500


# SEARCH STUDENT

@app.route("/students/search/<student_id>", methods=["GET"])
def search_student(student_id):
    try:
        with get_db_connection() as connection:
            student = connection.execute(
                "SELECT * FROM students WHERE student_id = ?",
                (student_id,)
            ).fetchone()

        if not student:
            return jsonify({"error": "Student not found"}), 404

        return jsonify(dict(student))

    except sqlite3.Error as error:
        app.logger.exception("Search student error")
        return jsonify({"error": str(error)}), 500


# UPDATE STUDENT

@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No update data received"}), 400

    try:
        with get_db_connection() as connection:
            existing = connection.execute(
                "SELECT * FROM students WHERE id = ?",
                (student_id,)
            ).fetchone()

            if not existing:
                return jsonify({"error": "Student not found"}), 404

            updated = {
                "student_id": str(data.get("student_id", existing["student_id"])).strip(),
                "name": str(data.get("name", existing["name"])).strip(),
                "program": str(data.get("program", existing["program"] or "")).strip(),
                "year": int(data.get("year", existing["year"] or 0)),
                "section": str(data.get("section", existing["section"] or "")).strip()
            }

            connection.execute("""
                UPDATE students
                SET student_id = ?, name = ?, program = ?,
                    year = ?, section = ?
                WHERE id = ?
            """, (
                updated["student_id"],
                updated["name"],
                updated["program"],
                updated["year"],
                updated["section"],
                student_id
            ))

        return jsonify({"message": "Student updated successfully!"})

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 409

    except (sqlite3.Error, ValueError, TypeError) as error:
        app.logger.exception("Update student error")
        return jsonify({"error": str(error)}), 500


# DELETE STUDENT

@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        with get_db_connection() as connection:
            result = connection.execute(
                "DELETE FROM students WHERE id = ?",
                (student_id,)
            )

            if result.rowcount == 0:
                return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student deleted successfully!"})

    except sqlite3.Error as error:
        app.logger.exception("Delete student error")
        return jsonify({"error": str(error)}), 500


# RETRIEVE PARTNER RECORDS

@app.route("/partner-records", methods=["GET"])
def get_partner_records():
    try:
        response = requests.get(
            f"{PARTNER_URL}/api/students",
            timeout=45
        )

        records = response.json()

        if not response.ok:
            return jsonify({
                "error": "Partner API request failed",
                "partner_status": response.status_code,
                "partner_response": records
            }), 502

        if isinstance(records, dict):
            records = records.get("students", records.get("data", []))

        if not isinstance(records, list):
            return jsonify({"error": "Invalid partner API response"}), 502

        return jsonify(records)

    except requests.RequestException as error:
        app.logger.exception("Partner API error")
        return jsonify({"error": str(error)}), 502

    except ValueError:
        return jsonify({"error": "Partner returned invalid JSON"}), 502


# SAVE SELECTED PARTNER RECORD TO LOCAL DATABASE

@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No student record received"}), 400

    try:
        student = prepare_student(data)

        if not student["student_id"] or not student["name"]:
            return jsonify({
                "error": "Student ID and name are required"
            }), 400

        with get_db_connection() as connection:
            connection.execute("""
                INSERT INTO students
                (student_id, name, program, year, section, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                student["student_id"],
                student["name"],
                student["program"],
                student["year"],
                student["section"],
                "Classmate API"
            ))

        return jsonify({
            "message": "Partner record successfully saved to your database!"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "This student record already exists in your database"
        }), 409

    except (sqlite3.Error, ValueError, TypeError) as error:
        app.logger.exception("Import student error")
        return jsonify({"error": str(error)}), 500


# SEND PRACTICE RECORD TO PARTNER

@app.route("/send-to-partner", methods=["POST"])
def send_to_partner():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No record received"}), 400

    try:
        student = prepare_student(data)

        if not student["student_id"] or not student["name"]:
            return jsonify({
                "error": "Student ID and name are required"
            }), 400

        response = requests.post(
            f"{PARTNER_URL}/api/students",
            json=student,
            timeout=45
        )

        try:
            partner_result = response.json()
        except ValueError:
            partner_result = response.text

        if not response.ok:
            return jsonify({
                "error": "Partner API rejected the record",
                "partner_status": response.status_code,
                "partner_response": partner_result
            }), 502

        return jsonify({
            "message": "Record successfully sent to partner!",
            "partner_response": partner_result
        })

    except requests.RequestException as error:
        app.logger.exception("Send to partner error")
        return jsonify({"error": str(error)}), 502

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


# GRADES API

@app.route("/grades/<student_id>", methods=["GET"])
def get_grades(student_id):
    try:
        with get_db_connection() as connection:
            grades = connection.execute(
                "SELECT * FROM grades WHERE student_id = ?",
                (student_id,)
            ).fetchall()

        return jsonify({
            "student_id": student_id,
            "grades": [
                {
                    "course": grade["course_title"] or grade["course_code"],
                    "grade": grade["grade"]
                }
                for grade in grades
            ]
        })

    except sqlite3.Error as error:
        app.logger.exception("Grades error")
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
