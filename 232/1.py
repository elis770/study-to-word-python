import requests

url = "https://www.sefaria.org/api/calendars"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)