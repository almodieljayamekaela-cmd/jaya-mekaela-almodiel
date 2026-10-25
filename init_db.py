
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

# Create the students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
""")

# Insert sample records only if the table is empty
cursor.execute("SELECT COUNT(*) FROM students")
count = cursor.fetchone()[0]

if count == 0:
    students = [
        ("2026-00123", "Juan Dela Cruz", "BSIT", 1, "A"),
        ("2026-00124", "Maria Santos", "BSIT", 1, "A"),
        ("2026-00125", "Pedro Reyes", "BSIT", 1, "B"),
        ("2026-00126", "Ana Garcia", "BSCS", 2, "A"),
        ("2026-00127", "Mark Rivera", "BSIT", 3, "C"),
        ("2026-00128", "Lea Mendoza", "BSCS", 2, "B")
    ]

    cursor.executemany("""
        INSERT INTO students
        (student_id, name, program, year, section)
        VALUES (?, ?, ?, ?, ?)
    """, students)

    print("Six sample students inserted successfully.")
else:
    print("Student records already exist. No sample records added.")

# Save and close the database
conn.commit()
conn.close()

print("Database initialized successfully.")
