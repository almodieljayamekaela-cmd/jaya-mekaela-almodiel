
import requests

url = "https://jaya-mekaela-almodiel.onrender.com"

response = requests.get(url)

print(response.text)
