
import requests

CLASSMATE_API_URL = input("Enter your classmate's Render URL: ").strip().rstrip("/")

ENDPOINT = input("Enter your classmate's endpoint (example: /student): ").strip()

if not ENDPOINT.startswith("/"):
    ENDPOINT = "/" + ENDPOINT

url = CLASSMATE_API_URL + ENDPOINT

try:
    response = requests.get(url, timeout=60)

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        print("Request successful!")
        try:
            print("API Data:")
            print(response.json())
        except ValueError:
            print("Response:", response.text)
    else:
        print("Request failed.")
        print("Response:", response.text)

except requests.RequestException as error:
    print("Connection error:", error)
