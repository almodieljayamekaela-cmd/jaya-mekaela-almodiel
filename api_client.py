
import requests

BASE_URL = "https://jaya-mekaela-almodiel.onrender.com"


def get_student():
    response = requests.get(f"{BASE_URL}/student", timeout=60)
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("\nSTUDENT INFORMATION")
        print("Student ID:", data["student_id"])
        print("Name:", data["name"])
        print("Program:", data["program"])
        print("Year:", data["year"])
        print("Section:", data["section"])
    else:
        print("Request failed:", response.text)


def say_hello():
    name = input("Enter your name: ")
    response = requests.get(
        f"{BASE_URL}/hello",
        params={"name": name},
        timeout=60
    )
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("\nGREETING")
        print(data["message"])
    else:
        print("Request failed:", response.text)


def get_course():
    response = requests.get(f"{BASE_URL}/course", timeout=60)
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("\nCOURSE INFORMATION")
        print("Course Code:", data["course_code"])
        print("Course Title:", data["course_title"])
        print("Instructor:", data["instructor"])
        print("Semester:", data["semester"])
        print("Academic Year:", data["academic_year"])
    else:
        print("Request failed:", response.text)


def greet_student():
    name = input("Enter your name: ")
    program = input("Enter your program: ")
    year = input("Enter your year: ")
    section = input("Enter your section: ")

    params = {
        "name": name,
        "program": program,
        "year": year,
        "section": section
    }

    response = requests.get(
        f"{BASE_URL}/greet",
        params=params,
        timeout=60
    )
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("\nPERSONALIZED GREETING")
        print(data["message"])
    else:
        print("Request failed:", response.text)


def get_profile():
    response = requests.get(f"{BASE_URL}/profile", timeout=60)
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("\nSTUDENT PROFILE")
        print("Student ID:", data["student_id"])
        print("Name:", data["name"])
        print("Program:", data["program"])
        print("Year:", data["year"])
        print("Section:", data["section"])
        print("Gmail:", data["gmail"])
    else:
        print("Request failed:", response.text)


def get_entertainment():
    response = requests.get(
        f"{BASE_URL}/entertainment",
        timeout=60
    )
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("\nENTERTAINMENT AND HOBBIES")
        print("Favorite Movie Genre:", data["favorite_movie"])
        print("Favorite Song:", data["favorite_song"])
        print("Favorite Game:", data["favorite_game"])
        print("Hobby:", data["hobby"])
    else:
        print("Request failed:", response.text)


def main():
    print("\nJAYA'S API CLIENT")
    print("1. Student Information")
    print("2. Hello Endpoint")
    print("3. Course Information")
    print("4. Personalized Greeting")
    print("5. Student Profile")
    print("6. Entertainment and Hobbies")

    choice = input("\nChoose an endpoint (1-6): ")

    try:
        if choice == "1":
            get_student()
        elif choice == "2":
            say_hello()
        elif choice == "3":
            get_course()
        elif choice == "4":
            greet_student()
        elif choice == "5":
            get_profile()
        elif choice == "6":
            get_entertainment()
        else:
            print("Invalid choice. Please choose 1-6.")

    except requests.RequestException as error:
        print("Connection error:", error)


if __name__ == "__main__":
    main()
