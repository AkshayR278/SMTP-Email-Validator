import requests
resp = requests.post("http://localhost:5000/validate", json={"email":"user...@example.com"})
print(resp.json())
