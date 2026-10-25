
import sqlite3
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Classmate API URL
CLASSMATE_API_URL = "https://maryjoydebaja.onrender.com/students"


# Connect to the database
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# HOME
@app.route("/")
def home():
    return render_template("index.html")


# STUDENT PROFILE
@app.route("/student")
def student():
    return jsonify({
        "student_id": "24-00328",
        "name": "Jaya Mekaela Almodiel",
        "program": "BSIT",
        "year": "3rd Year",
        "section": "Hamilton"
    })


# HELLO
@app.route("/hello")
def hello():
    return jsonify({"message": "Hello, World!"})


# COURSE INFORMATION
@app.route("/course")
def course():
    return jsonify({
        "course_code": "3120",
        "course_title": "System Integration",
        "instructor": "Dr. Rene Arduo",
        "semester": "1st Semester",
        "academic_year": "2026-2027"
    })


# GREET
@app.route("/greet")
def greet():
    name = request.args.get("name", "Student")
    return jsonify({"message": f"Hello, {name}!"})


# PERSONAL PROFILE
@app.route("/profile")
def profile():
    return jsonify({
        "name": "Jaya Mekaela Almodiel",
        "favorites": [
            "Horror",
            "Palayo sa Mundo",
            "Mobile Legends"
        ],
        "hobby": "Watching movies and reading books"
    })


# GET ALL STUDENTS
@app.route("/students", methods=["GET"])
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students ORDER BY id"
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# GET ONE STUDENT
@app.route("/students/<int:id>", methods=["GET"])
def get_student_by_id(id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# GET STUDENTS BY PROGRAM
@app.route("/students/program/<program>", methods=["GET"])
def get_students_by_program(program):
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students WHERE program = ?", (program,)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# CREATE STUDENT - POST
@app.route("/students", methods=["POST"])
def create_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Please send student information as JSON."}), 400

    required_fields = [
        "student_id", "name", "program", "year", "section"
    ]

    if any(
        field not in data or str(data[field]).strip() == ""
        for field in required_fields
    ):
        return jsonify({
            "error": "All fields are required: student_id, name, program, year, section."
        }), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number."}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        """INSERT INTO students
        (student_id, name, program, year, section)
        VALUES (?, ?, ?, ?, ?)""",
        (
            str(data["student_id"]).strip(),
            str(data["name"]).strip(),
            str(data["program"]).strip(),
            year,
            str(data["section"]).strip()
        )
    )

    conn.commit()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()

    conn.close()

    return jsonify({
        "message": "Student added successfully.",
        "student": dict(student)
    }), 201


# UPDATE STUDENT - PUT
@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Please send updated information as JSON."}), 400

    required_fields = [
        "student_id", "name", "program", "year", "section"
    ]

    if any(
        field not in data or str(data[field]).strip() == ""
        for field in required_fields
    ):
        return jsonify({
            "error": "Send all five fields to update the student."
        }), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number."}), 400

    conn = get_db_connection()

    existing = conn.execute(
        "SELECT id FROM students WHERE id = ?", (id,)
    ).fetchone()

    if existing is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    conn.execute(
        """UPDATE students
        SET student_id = ?, name = ?, program = ?, year = ?, section = ?
        WHERE id = ?""",
        (
            str(data["student_id"]).strip(),
            str(data["name"]).strip(),
            str(data["program"]).strip(),
            year,
            str(data["section"]).strip(),
            id
        )
    )

    conn.commit()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()

    conn.close()

    return jsonify({
        "message": "Student updated successfully.",
        "student": dict(student)
    })


# DELETE STUDENT - DELETE
@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()

    if student is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Student deleted successfully.",
        "deleted_student": dict(student)
    })


# GET CLASSMATE STUDENTS FROM EXTERNAL API
@app.route("/classmate-students", methods=["GET"])
def get_classmate_students():
    try:
        response = requests.get(CLASSMATE_API_URL, timeout=60)

        if response.status_code != 200:
            return jsonify({
                "error": "Could not retrieve classmate records.",
                "status_code": response.status_code
            }), 502

        return jsonify({
            "message": "Classmate records retrieved successfully.",
            "students": response.json()
        })

    except requests.RequestException as error:
        return jsonify({
            "error": "Could not connect to the classmate API.",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({
            "error": "The classmate API did not return valid JSON."
        }), 502


# RUN THE APP
if __name__ == "__main__":
    app.run(debug=True)
