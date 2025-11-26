import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Define the scopes (permissions) your program needs.
# 'documents' allows the program to create and modify Google Docs.
# 'drive.metadata' is needed to see the file you create.
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.metadata"]

def add_text_to_doc(doc_id, text_to_add, docs_service):
    """
    Adds text to an existing Google Doc at the end.

    Args:
        doc_id: The ID of the document to modify.
        text_to_add: A string of text to insert into the document.
        docs_service: An authenticated Google Docs API service object.
    """
    try:
        # First, get the current state of the document to find the total length.
        document = docs_service.documents().get(documentId=doc_id).execute()
        document_length = document['body']['content'][-1]['endIndex'] - 1

        # Create the 'requests' body for the batchUpdate call.
        requests = [
            {
                'insertText': {
                    'location': {
                        # A more robust approach is to find the current end of the document.
                        'index': document_length
                    },
                    'text': text_to_add
                }
            }
        ]

        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()

        print(f"Successfully added text to the document with ID: {doc_id}")
    except Exception as e:
        print(f"An error occurred while adding text: {e}")

def format_text_in_doc(doc_id, docs_service, start_index, end_index):
    """
    Formats text in an existing Google Doc to be bold.

    Args:
        doc_id: The ID of the document to modify.
        docs_service: An authenticated Google Docs API service object.
        start_index: The starting index (position) of the text to format.
        end_index: The ending index (position) of the text to format.
    """
    # The 'updateTextStyle' request formats the text.
    requests = [
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'textStyle': {
                    'bold': True
                },
                'fields': 'bold'
            }
        }
    ]

    try:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        print(f"Successfully formatted text in the document with ID: {doc_id}")
    except Exception as e:
        print(f"An error occurred while formatting text: {e}")

def main():
    """
    Creates a new Google Doc, adds some text, and then formats it.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        docs_service = build("docs", "v1", credentials=creds)

        # ------------------------------------------------------------------
        # --- Part 1: Create a new document and add text ---
        # ------------------------------------------------------------------
        doc_title = "My Document with Formatted Text"
        body = {'title': doc_title}
        new_doc = docs_service.documents().create(body=body).execute()
        doc_id = new_doc.get('documentId')

        print(f"Created document with title: {new_doc.get('title')}")
        print(f"Document ID: {doc_id}")
        print(f"Document URL: https://docs.google.com/document/d/{doc_id}/edit")

        with open(r"C:\Users\Usuario\Documents\random\emofile.txt", encoding="utf-8") as f:
            Text = f.read()
        # Text to be added to the document.
        text_to_format = Text
        additional_text = "\nThis is a normal paragraph."

        # Add the text to the document.
        add_text_to_doc(doc_id, text_to_format, docs_service)
        add_text_to_doc(doc_id, additional_text, docs_service)

        # ------------------------------------------------------------------
        # --- Part 2: Format the added text ---
        # ------------------------------------------------------------------
        # A more robust approach is to fetch the document content to find the correct indices.
        # This prevents the 'index out of bounds' error.
        document = docs_service.documents().get(documentId=doc_id).execute()
        content = document.get('body').get('content')

        # Find the text in the document's content to get the correct indices.
        # The first paragraph usually contains the title and a newline, so we start looking
        # from the second element of the content list.
        text_to_find = text_to_format
        start_index = -1
        end_index = -1

        for element in content:
            if 'paragraph' in element:
                for text_run in element['paragraph']['elements']:
                    if 'textRun' in text_run and text_run['textRun']['content'].strip() == text_to_find:
                        start_index = text_run['startIndex']
                        end_index = text_run['endIndex']
                        break
            if start_index != -1:
                break

        if start_index != -1 and end_index != -1:
            format_text_in_doc(doc_id, docs_service, start_index, end_index)
        else:
            print(f"Could not find the text '{text_to_find}' in the document to format.")


    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
