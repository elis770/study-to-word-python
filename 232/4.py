import requests

url = "https://www.sefaria.org/api/calendars"

# Make a GET request to the URL
response = requests.get(url)
# Parse the response as JSON
data = response.json()
# Retrieve the list of calendar_items
calendar_items = data['calendar_items']

for item in calendar_items:
    if item["title"]["en"] == "Daily Rambam":
        perek_ref = item["ref"]
        perek_name = item["displayValue"]["en"]
        break
url = f"https://www.sefaria.org/api/v3/texts/{perek_ref}"

# Make GET request
response = requests.get(url)

# Parse response as JSON 
data = response.json() 

perek = data['versions'][0]['text']

print(', '.join(perek))  # Print the entire JSON response