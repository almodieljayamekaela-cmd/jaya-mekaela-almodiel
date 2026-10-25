
import os
import sqlite3
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.db")
CLASSMATE_API_URL = "https://maryjoydebaja.onrender.com/students"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the table if needed and add missing columns."""
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            name TEXT,
            program TEXT,
            year TEXT,
            section TEXT
        )
    """)

    existing = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(students)").fetchall()
    }

    # Add missing fields without deleting existing records.
    for column in ["student_id", "name", "program", "year", "section"]:
        if column not in existing:
            conn.execute(f'ALTER TABLE students ADD COLUMN "{column}" TEXT')

    conn.commit()
    conn.close()


def get_student_fields():
    conn = get_db()
    fields = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(students)").fetchall()
    }
    conn.close()
    return fields


@app.before_request
def prepare_database():
    init_db()


def error_response(message, status=500):
    return jsonify({"error": message}), status


# ---------------- HOME AND BASIC APIS ----------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/hello")
def hello():
    return jsonify({"message": "Hello! Welcome to my Student API."})


@app.route("/student")
def student():
    return jsonify({
        "student_id": "24-00328",
        "name": "Jaya Mekaela Almodiel",
        "program": "BSIT",
        "year": "3rd Year",
        "section": "Hamilton"
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
        "student": {
            "student_id": "24-00328",
            "name": "Jaya Mekaela Almodiel",
            "program": "BSIT",
            "year": "3rd Year",
            "section": "Hamilton"
        },
        "course": {
            "course_code": "IT3120",
            "course_title": "System Integration",
            "instructor": "Dr. Rene Arduo"
        }
    })


# ---------------- GET ALL STUDENTS ----------------

@app.route("/students", methods=["GET"])
def get_students():
    try:
        conn = get_db()
        rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows]), 200

    except sqlite3.Error as e:
        app.logger.exception("Could not retrieve students")
        return error_response(f"Database error: {e}")


# ---------------- SEARCH BY STUDENT ID ----------------

@app.route("/students/search/<string:student_id>")
def search_student(student_id):
    try:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()
        conn.close()

        if row is None:
            return error_response("Student not found.", 404)

        return jsonify(dict(row)), 200

    except sqlite3.Error as e:
        app.logger.exception("Student search failed")
        return error_response(f"Database error: {e}")


# ---------------- GET STUDENT BY DATABASE ID ----------------

@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    try:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()
        conn.close()

        if row is None:
            return error_response("Student not found.", 404)

        return jsonify(dict(row)), 200

    except sqlite3.Error as e:
        app.logger.exception("Get student failed")
        return error_response(f"Database error: {e}")


# ---------------- FILTER BY PROGRAM ----------------

@app.route("/students/program/<string:program>")
def students_by_program(program):
    try:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM students WHERE program = ?", (program,)
        ).fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows]), 200

    except sqlite3.Error as e:
        app.logger.exception("Program filter failed")
        return error_response(f"Database error: {e}")


# ---------------- ADD STUDENT ----------------

@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("Please submit student information as JSON.", 400)

    fields = ["student_id", "name", "program", "year", "section"]
    student = {}

    for field in fields:
        value = data.get(field)

        if value is None or not str(value).strip():
            return error_response(f"Please provide {field}.", 400)

        student[field] = str(value).strip()

    try:
        conn = get_db()

        # Check actual table columns before inserting.
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(students)").fetchall()
        }

        missing = [field for field in fields if field not in columns]
        if missing:
            conn.close()
            return error_response(
                "The database is missing these columns: " + ", ".join(missing)
            )

        conn.execute("""
            INSERT INTO students
                (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        """, tuple(student[field] for field in fields))

        conn.commit()

        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student["student_id"],)
        ).fetchone()

        conn.close()

        return jsonify({
            "message": "Student added successfully!",
            "student": dict(row)
        }), 201

    except sqlite3.IntegrityError:
        return error_response(
            "This student ID already exists. Please use a different ID.", 409
        )

    except sqlite3.Error as e:
        app.logger.exception("Add student failed")
        return error_response(f"Database error while adding student: {e}")


# ---------------- EDIT STUDENT ----------------

@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("Please submit updated information as JSON.", 400)

    allowed = ["student_id", "name", "program", "year", "section"]
    updates = {}

    for field in allowed:
        if field in data:
            value = data[field]

            if value is None or not str(value).strip():
                return error_response(f"{field} cannot be empty.", 400)

            updates[field] = str(value).strip()

    if not updates:
        return error_response("No fields were provided to update.", 400)

    try:
        conn = get_db()

        existing = conn.execute(
            "SELECT id FROM students WHERE id = ?", (id,)
        ).fetchone()

        if existing is None:
            conn.close()
            return error_response("Student not found.", 404)

        columns = get_columns_from_connection(conn)
        missing = [field for field in updates if field not in columns]

        if missing:
            conn.close()
            return error_response(
                "Database is missing columns: " + ", ".join(missing)
            )

        set_clause = ", ".join(f'"{field}" = ?' for field in updates)
        values = list(updates.values()) + [id]

        conn.execute(
            f"UPDATE students SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

        conn.close()

        return jsonify({
            "message": "Student updated successfully!",
            "student": dict(row)
        }), 200

    except sqlite3.IntegrityError:
        return error_response("That student ID is already in use.", 409)

    except sqlite3.Error as e:
        app.logger.exception("Update student failed")
        return error_response(f"Database error: {e}")


def get_columns_from_connection(conn):
    return {
        row["name"]
        for row in conn.execute("PRAGMA table_info(students)").fetchall()
    }


# ---------------- DELETE STUDENT ----------------

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    try:
        conn = get_db()

        result = conn.execute(
            "DELETE FROM students WHERE id = ?", (id,)
        )

        conn.commit()
        deleted = result.rowcount
        conn.close()

        if deleted == 0:
            return error_response("Student not found.", 404)

        return jsonify({"message": "Student deleted successfully!"}), 200

    except sqlite3.Error as e:
        app.logger.exception("Delete student failed")
        return error_response(f"Database error: {e}")


# ---------------- GRADES API ----------------

@app.route("/grades/<string:student_id>")
def grades(student_id):
    try:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        conn.close()

        if row is None:
            return error_response("Student not found.", 404)

        return jsonify({
            "student_id": student_id,
            "student_name": row["name"],
            "grades": [
                {"course_code": "IT3110", "grade": 1.25},
                {"course_code": "IT3120", "grade": 1.50},
                {"course_code": "IT3130", "grade": 1.25}
            ],
            "note": "Sample grades for demonstration only, not official records."
        }), 200

    except sqlite3.Error as e:
        app.logger.exception("Grades request failed")
        return error_response(f"Database error: {e}")


# ---------------- CLASSMATE API ----------------

@app.route("/classmate-students")
def classmate_students():
    try:
        response = requests.get(CLASSMATE_API_URL, timeout=15)
        response.raise_for_status()

        return jsonify({
            "message": "Classmate API data retrieved successfully.",
            "students": response.json()
        }), 200

    except requests.exceptions.RequestException as e:
        app.logger.exception("Classmate API request failed")
        return jsonify({
            "error": "Could not retrieve classmate data.",
            "details": str(e)
        }), 502

    except ValueError:
        return error_response("Classmate API returned invalid JSON.", 502)


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
