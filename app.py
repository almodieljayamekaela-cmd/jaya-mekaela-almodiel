from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def home():
    return "Welcome to Jaya's API!"


@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00328",
        "name": "Jaya Mekaela Almodiel",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Jaya Mekaela Almodiel')
    return jsonify({
        "message": f"Hello, {name}!"
    })


@app.route('/course')
def say_course():
    return jsonify({
        "course_code": "IT3120",
        "course_title": "System Integration",
        "instructor": "Dr. Rene Arduo",
        "semester": "First Semester",
        "academic_year": "AY 2026-2027"
    })


@app.route('/greet')
def greet():
    name = request.args.get('name', 'Jaya Mekaela Almodiel')
    program = request.args.get('program', 'BSIT')
    year = request.args.get('year', '3')
    section = request.args.get('section', 'A')

    return jsonify({
        "message": f"Hello {name} from {program} {year} {section}!"
    })

@app.route('/profile')
def get_profile():
    return jsonify({
        "student_id": "24-00328",
        "name": "Jaya Mekaela Almodiel",
        "program": "BSIT",
        "year": 3,
        "section": "A",
        "gmail": "almodieljayamekaela@isufst.edu.ph",
    })

@app.route('/entertainment')
def get_entertainment():
    return jsonify({
        "favorite_movie": "horror",
        "favorite_song": "palayo sa mundo",
        "favorite_game": "Mobile Legends",
        "hobby": "Watching movies and reading books"
    })
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

