
import os
import sqlite3
import requests

from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Database configuration
DATABASE = "students.db"

# Classmate API
CLASSMATE_API_URL = "https://maryjoydebaja.onrender.com/students"

# Your student information
STUDENT_INFO = {
    "student_id": "24-00328",
    "name": "Jaya Mekaela Almodiel",
    "program": "BSIT",
    "year": "3rd Year",
    "section": "Hamilton"
}

COURSE_INFO = {
    "course_code": "IT3120",
    "course_title": "System Integration",
    "instructor": "Dr. Rene Arduo",
    "semester": "1st Semester",
    "academic_year": "2026-2027"
}


# ----------------------------------------
# DATABASE CONNECTION
# ----------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    return dict(row) if row else None


# ----------------------------------------
# HOME PAGE
# ----------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------------------
# BASIC API ENDPOINTS
# ----------------------------------------

@app.route("/student", methods=["GET"])
def student():
    return jsonify(STUDENT_INFO)


@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({
        "message": "Hello! Welcome to my Student API."
    })


@app.route("/course", methods=["GET"])
def course():
    return jsonify(COURSE_INFO)


@app.route("/greet", methods=["GET"])
def greet():
    name = request.args.get("name", "Student")
    return jsonify({
        "message": f"Hello, {name}!"
    })


@app.route("/profile", methods=["GET"])
def profile():
    return jsonify({
        "student": STUDENT_INFO,
        "course": COURSE_INFO
    })


# ----------------------------------------
# GET ALL STUDENTS
# ----------------------------------------

@app.route("/students", methods=["GET"])
def get_students():
    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM students"
        ).fetchall()
        conn.close()

        return jsonify([dict(row) for row in rows]), 200

    except sqlite3.Error as error:
        return jsonify({
            "error": "Could not retrieve students.",
            "details": str(error)
        }), 500


# ----------------------------------------
# SEARCH STUDENT BY STUDENT ID
# ----------------------------------------

@app.route("/students/search/<string:student_id>", methods=["GET"])
def search_student(student_id):
    try:
        conn = get_db_connection()

        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        conn.close()

        if row is None:
            return jsonify({
                "error": "Student not found."
            }), 404

        return jsonify(dict(row)), 200

    except sqlite3.Error as error:
        return jsonify({
            "error": str(error)
        }), 500


# ----------------------------------------
# GET STUDENT BY DATABASE ID
# ----------------------------------------

@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    try:
        conn = get_db_connection()

        row = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        conn.close()

        if row is None:
            return jsonify({
                "error": "Student not found."
            }), 404

        return jsonify(dict(row)), 200

    except sqlite3.Error as error:
        return jsonify({
            "error": str(error)
        }), 500


# ----------------------------------------
# FILTER STUDENTS BY PROGRAM
# ----------------------------------------

@app.route("/students/program/<string:program>", methods=["GET"])
def get_students_by_program(program):
    try:
        conn = get_db_connection()

        rows = conn.execute(
            "SELECT * FROM students WHERE program = ?",
            (program,)
        ).fetchall()

        conn.close()

        return jsonify([dict(row) for row in rows]), 200

    except sqlite3.Error as error:
        return jsonify({
            "error": str(error)
        }), 500


# ----------------------------------------
# ADD A STUDENT
# ----------------------------------------

@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Please provide student information in JSON format."
        }), 400

    required_fields = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    missing_fields = [
        field for field in required_fields
        if not str(data.get(field, "")).strip()
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields.",
            "missing_fields": missing_fields
        }), 400

    try:
        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["student_id"].strip(),
                data["name"].strip(),
                data["program"].strip(),
                data["year"].strip(),
                data["section"].strip()
            )
        )

        conn.commit()

        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (data["student_id"].strip(),)
        ).fetchone()

        conn.close()

        return jsonify({
            "message": "Student added successfully.",
            "student": row_to_dict(row)
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Could not add student. The student ID may already exist."
        }), 409

    except sqlite3.Error as error:
        return jsonify({
            "error": str(error)
        }), 500


# ----------------------------------------
# UPDATE A STUDENT
# ----------------------------------------

@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Please provide updated information in JSON format."
        }), 400

    allowed_fields = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    updates = {
        field: data[field]
        for field in allowed_fields
        if field in data
    }

    if not updates:
        return jsonify({
            "error": "No valid fields provided for updating."
        }), 400

    for field, value in updates.items():
        if not isinstance(value, str) or not value.strip():
            return jsonify({
                "error": f"{field} must be a non-empty string."
            }), 400
        updates[field] = value.strip()

    try:
        conn = get_db_connection()

        existing = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if existing is None:
            conn.close()
            return jsonify({
                "error": "Student not found."
            }), 404

        set_clause = ", ".join(
            f"{field} = ?" for field in updates
        )

        values = list(updates.values())
        values.append(id)

        conn.execute(
            f"UPDATE students SET {set_clause} WHERE id = ?",
            values
        )

        conn.commit()

        updated = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        conn.close()

        return jsonify({
            "message": "Student updated successfully.",
            "student": row_to_dict(updated)
        }), 200

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Could not update student. The student ID may already exist."
        }), 409

    except sqlite3.Error as error:
        return jsonify({
            "error": str(error)
        }), 500


# ----------------------------------------
# DELETE A STUDENT
# ----------------------------------------

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    try:
        conn = get_db_connection()

        existing = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if existing is None:
            conn.close()
            return jsonify({
                "error": "Student not found."
            }), 404

        conn.execute(
            "DELETE FROM students WHERE id = ?",
            (id,)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Student deleted successfully."
        }), 200

    except sqlite3.Error as error:
        return jsonify({
            "error": str(error)
        }), 500


# ----------------------------------------
# GRADES API
# ----------------------------------------

@app.route("/grades/<string:student_id>", methods=["GET"])
def get_grades(student_id):
    try:
        conn = get_db_connection()

        student_record = conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        conn.close()

        if student_record is None:
            return jsonify({
                "error": "Student not found."
            }), 404

        # Example grades for demonstration only.
        # These are not official academic records.
        grades = [
            {"course_code": "IT3110", "grade": 1.25},
            {"course_code": "IT3120", "grade": 1.50},
            {"course_code": "IT3130", "grade": 1.25}
        ]

        return jsonify({
            "student_id": student_id,
            "student_name": student_record["name"],
            "grades": grades,
            "note": "Sample grades for demonstration only."
        }), 200

    except sqlite3.Error as error:
        return jsonify({
            "error": str(error)
        }), 500


# ----------------------------------------
# CLASSMATE API
# ----------------------------------------

@app.route("/classmate-students", methods=["GET"])
def get_classmate_students():
    try:
        response = requests.get(
            CLASSMATE_API_URL,
            timeout=15
        )

        response.raise_for_status()

        return jsonify({
            "message": "Classmate API data retrieved successfully.",
            "students": response.json()
        }), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "The classmate API request timed out. Please try again."
        }), 504

    except requests.exceptions.RequestException as error:
        return jsonify({
            "error": "Could not connect to the classmate API.",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({
            "error": "The classmate API returned invalid JSON."
        }), 502


# ----------------------------------------
# RENDER CONFIGURATION
# ----------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
