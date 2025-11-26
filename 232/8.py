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

def align_text_in_doc(doc_id, docs_service, start_index, end_index):
    """
    Aligns text in an existing Google Doc to the right.

    Args:
        doc_id: The ID of the document to modify.
        docs_service: An authenticated Google Docs API service object.
        start_index: The starting index (position) of the text to align.
        end_index: The ending index (position) of the text to align.
    """
    # The 'updateParagraphStyle' request formats the paragraph.
    requests = [
        {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'paragraphStyle': {
                    'alignment': 'END'
                },
                'fields': 'alignment'
            }
        }
    ]

    try:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        print(f"Successfully aligned text to the right in the document with ID: {doc_id}")
    except Exception as e:
        print(f"An error occurred while aligning text: {e}")

def main():
    """
    Creates a new Google Doc, adds some text, formats, and aligns it.
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
        text_to_format_right = "\nThis text will be aligned to the right."

        # Add the text to the document.
        add_text_to_doc(doc_id, text_to_format, docs_service)
        add_text_to_doc(doc_id, additional_text, docs_service)
        add_text_to_doc(doc_id, text_to_format_right, docs_service)

        # ------------------------------------------------------------------
        # --- Part 2: Format the added text and align it ---
        # ------------------------------------------------------------------
        # A more robust approach is to fetch the document content to find the correct indices.
        # This prevents the 'index out of bounds' error.
        document = docs_service.documents().get(documentId=doc_id).execute()
        content = document.get('body').get('content')

        # Find the text in the document's content to get the correct indices.
        text_to_find_bold = text_to_format
        text_to_find_right = text_to_format_right.strip()

        start_index_bold = -1
        end_index_bold = -1
        start_index_right = -1
        end_index_right = -1

        for element in content:
            if 'paragraph' in element:
                for text_run in element['paragraph']['elements']:
                    if 'textRun' in text_run:
                        if text_run['textRun']['content'].strip() == text_to_find_bold:
                            start_index_bold = text_run['startIndex']
                            end_index_bold = text_run['endIndex']
                        elif text_run['textRun']['content'].strip() == text_to_find_right:
                            start_index_right = text_run['startIndex']
                            end_index_right = text_run['endIndex']

        if start_index_bold != -1 and end_index_bold != -1:
            align_text_in_doc(doc_id, docs_service, start_index_bold, end_index_bold)
        else:
            print(f"Could not find the text '{text_to_find_bold}' in the document to format.")

        if start_index_right != -1 and end_index_right != -1:
            align_text_in_doc(doc_id, docs_service, start_index_right, end_index_right)
        else:
            print(f"Could not find the text '{text_to_find_right}' in the document to align.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()