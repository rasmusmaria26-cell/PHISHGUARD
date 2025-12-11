import requests
import json

url = "http://127.0.0.1:8000/analyze"
data = {
    "url": "https://www.google.com",
    "text": "test page",
    "deceptive_links_count": 0
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
