import requests
import urllib.parse

API_URL = "http://127.0.0.1:8000"

r = requests.post(API_URL + "/session")
print(token := r.json()["session_token"])

r = requests.get(API_URL + "/session?token=" + urllib.parse.quote(token))
print(r.json())

r = requests.post(API_URL + "/address/?token=" + urllib.parse.quote(token) + "&label=" + urllib.parse.quote("Notre Dame Paris"))
print(response := r.json())

r = requests.post(API_URL + "/address/?token=" + urllib.parse.quote(token) + "&label=" + urllib.parse.quote("Panthéon Paris"))
print(response := r.json())

r = requests.post(API_URL + "/address/?token=" + urllib.parse.quote(token) + "&label=" + urllib.parse.quote("Tour Eiffel Paris"))
print(response := r.json())

r = requests.get(API_URL + "/graph/?token=" + urllib.parse.quote(token))
print(response := r.json())
