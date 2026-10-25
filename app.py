
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# LAB 6: Home Page
@app.route("/")
def home():
    return render_template("index.html")


# LAB 6: Student Information
@app.route("/student")
def student():
    return jsonify({
        "student_id": "24-00328",
        "name": "Jaya Mekaela Almodiel",
        "program": "BSIT",
        "year": "3rd Year",
        "section": "Hamilton"
    })


# LAB 6: Hello API
@app.route("/hello")
def hello():
    return jsonify({
        "message": "Hello, World!"
    })


# LAB 6: Course Information
@app.route("/course")
def course():
    return jsonify({
        "course_code": "3120",
        "course_title": "System Integration",
        "instructor": "Dr. Rene Arduo",
        "semester": "1st Semester",
        "academic_year": "2026-2027"
    })


# LAB 6: Greeting API
@app.route("/greet")
def greet():
    name = request.args.get("name", "Student")
    return jsonify({
        "message": f"Hello, {name}!"
    })


# LAB 6: Profile API
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


# LAB 7: Retrieve All Students from SQLite
@app.route("/students")
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# LAB 7: Retrieve One Student by ID
@app.route("/students/<int:id>")
def get_student_by_id(id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# LAB 7: Filter Students by Program
@app.route("/students/program/<program>")
def get_students_by_program(program):
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students WHERE program = ?",
        (program,)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
