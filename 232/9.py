import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scopes (permissions) your program needs.
# 'documents' allows the program to create and modify Google Docs.
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.metadata"]

def main():
    """
    A simpler script that creates a Google Doc, adds text, formats, and aligns it.
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
        # --- Create a new document ---
        # ------------------------------------------------------------------
        doc_title = "Simplified Python-Generated Doc"
        new_doc = docs_service.documents().create(body={'title': doc_title}).execute()
        doc_id = new_doc.get('documentId')

        print(f"Created document with title: {new_doc.get('title')}")
        print(f"Document ID: {doc_id}")
        print(f"Document URL: https://docs.google.com/document/d/{doc_id}/edit")

        # ------------------------------------------------------------------
        # --- Define and add all text at once ---
        # ------------------------------------------------------------------
        text_to_format = "This text will be bold.\n"
        additional_text = "This is a normal paragraph.\n"
        text_to_format_right = "This text will be aligned to the right.\n"
        
        # Combine all the text into a single string.
        full_text = text_to_format + additional_text + text_to_format_right

        # The 'insertText' request adds the full text.
        insert_request = {
            'insertText': {
                'location': {
                    'index': 1  # Index 1 is always the start of the document content.
                },
                'text': full_text
            }
        }
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': [insert_request]}).execute()
        print("\nSuccessfully added all text to the document.")

        # ------------------------------------------------------------------
        # --- Format the first paragraph (bold) ---
        # ------------------------------------------------------------------
        # We know the first line is the text to be bold, so we can use its length to find the end index.
        bold_request = {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': len(text_to_format) + 1  # Add 1 for the new line character.
                },
                'textStyle': {
                    'bold': True
                },
                'fields': 'bold'
            }
        }
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': [bold_request]}).execute()
        print("Successfully formatted text to be bold.")

        # ------------------------------------------------------------------
        # --- Align the last paragraph to the right ---
        # ------------------------------------------------------------------
        # We get the end of the document to find the correct range for the last paragraph.
        document = docs_service.documents().get(documentId=doc_id).execute()
        end_of_doc_index = document['body']['content'][-1]['endIndex']
        
        # The start index is the end of the second paragraph.
        start_of_last_para = len(text_to_format) + len(additional_text) + 1

        align_request = {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start_of_last_para,
                    'endIndex': end_of_doc_index -1
                },
                'paragraphStyle': {
                    'alignment': 'END'
                },
                'fields': 'alignment'
            }
        }
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': [align_request]}).execute()
        print("Successfully aligned text to the right.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()