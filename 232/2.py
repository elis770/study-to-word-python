import requests
from docx import Document

# --- Step 1: Fetch the Daily Rambam reference from the Sefaria calendar API ---

# Define the URL for the Sefaria calendar API
url = "https://www.sefaria.org/api/calendars"

# Make a GET request to the URL
response = requests.get(url)

# Parse the JSON response
data = response.json()

# Retrieve the list of calendar items
calendar_items = data['calendar_items']
print(calendar_items)
# Find the dictionary for the "Daily Rambam" and store its reference and display name
for item in calendar_items:
    if item['title']['en'] == 'Daily Rambam':
        parasha_ref = item['ref'] 
        parasha_name = item['displayValue']['en']
        break

# Extract the base reference (removes the specific section part)
parasha_ref = parasha_ref.split("-")[0] 

# --- Step 2: Fetch the Hebrew and English text for the retrieved reference ---

# Construct the URL for the Sefaria text API with the specific reference
url = f"https://www.sefaria.org/api/v3/texts/{parasha_ref}"

# Make the GET request
response = requests.get(url)

# Parse the JSON response
data = response.json() 

# Extract the version title and text for the Hebrew version
he_vtitle = data['versions'][0]['versionTitle'] 
he_pasuk = data['versions'][0]['text']

# Construct a new URL to get the English version of the text
url = f"https://www.sefaria.org/api/v3/texts/{parasha_ref}?version=english"

# Make the GET request for the English version
response = requests.get(url)

# Parse the JSON response
data = response.json()

# Retrieve the version title and text for the English version
en_vtitle = data['versions'][0]['versionTitle']
en_pasuk = data['versions'][0]['text']

# --- Step 3: Fetch related commentaries for the text ---

# Construct the URL to find texts linked to our reference
url = f"https://www.sefaria.org/api/related/{parasha_ref}"

# Make the GET request
response = requests.get(url)

# Parse the JSON response
data = response.json()

# Initialize an empty list to store commentary references
commentaries = []

# Iterate through the linked texts and filter for commentaries
for linked_text in data["links"]:
    if linked_text['type'] == 'commentary':
        commentaries.append(linked_text['ref'])

# --- Step 4: Define a function to get the text of a commentary ---

def get_commentary_text(ref):
    """
    Fetches the title and text of a commentary given its reference.

    Args:
        ref (str): The Sefaria reference for the commentary (e.g., "Rashi on Genesis 1:1:1").

    Returns:
        tuple: A tuple containing the title (str) and the text (str) of the commentary,
               or None if no primary version is found.
    """
    # Construct the URL for the Sefaria text API with the commentary reference
    url = f"https://www.sefaria.org/api/v3/texts/{ref}"
    response = requests.get(url)
    data = response.json()

    # Check if a primary version of the commentary exists
    if "versions" in data and len(data['versions']) > 0:
      
      # Retrieve the title and text of the commentary
      title = data['title']
      text = data['versions'][0]['text']

      # Return the title and the text
      return title, text
    return None, None # Return None if no version is found

# --- Step 5: Fetch the text of the first three commentaries ---

# Get the title and text for the first three commentaries from the list
com1_title, com1_text = get_commentary_text(commentaries[0])
com2_title, com2_text = get_commentary_text(commentaries[1])
com3_title, com3_text = get_commentary_text(commentaries[2])

# --- Step 6: Process and save the Hebrew text ---

# Clean up the Hebrew text by removing HTML tags and extra characters
resultb = str(he_pasuk).replace("<small>", "").replace("</small>", "").replace("']", "").replace("['", "")

# Create a new Word document
document = Document()

# Add a heading to the document
document.add_heading('My First Document', level=1)

# Add the cleaned Hebrew text as a paragraph
document.add_paragraph(resultb)

# Save the Word document
document.save('my_new_document2.docx')

# --- Step 7: Write the Hebrew text to a text file and print it ---

# Open a text file in write mode with UTF-8 encoding
with open("emofile.txt", "w", encoding="utf-8") as f: 
    f.write(resultb)  # Write the cleaned Hebrew verse to the file

# Open and read the file to verify its contents
with open("emofile.txt", encoding="utf-8") as f:
  print(f.read())