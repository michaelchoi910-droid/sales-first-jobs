"""Google Docs API client for uploading interview analysis documents"""

import os
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re


class GoogleDocsClient:
    """Client for creating and managing Google Docs"""

    SCOPES = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file'
    ]

    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Docs client

        Args:
            credentials_path: Path to service account JSON credentials file.
                            If None, will try to get from GOOGLE_CREDENTIALS_PATH env var
        """
        credentials_path = credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        if not credentials_path:
            raise ValueError(
                "Google credentials path is required. "
                "Set GOOGLE_CREDENTIALS_PATH environment variable."
            )

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

        # Load credentials
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=self.SCOPES
        )

        # Build API clients
        self.docs_service = build('docs', 'v1', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

    def create_document(self, title: str) -> str:
        """
        Create a new Google Doc

        Args:
            title: Title of the document

        Returns:
            Document ID
        """
        try:
            document = self.docs_service.documents().create(body={'title': title}).execute()
            doc_id = document.get('documentId')
            print(f"📄 Created Google Doc: {title}")
            print(f"   Document ID: {doc_id}")
            return doc_id

        except HttpError as error:
            print(f"❌ Error creating document: {error}")
            raise

    def insert_text(self, document_id: str, text: str, index: int = 1):
        """
        Insert text into a document at a specific index

        Args:
            document_id: The document ID
            text: Text to insert
            index: Position to insert (1 is start of document)
        """
        try:
            requests = [{
                'insertText': {
                    'location': {'index': index},
                    'text': text
                }
            }]

            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()

        except HttpError as error:
            print(f"❌ Error inserting text: {error}")
            raise

    def markdown_to_google_docs(self, document_id: str, markdown_content: str):
        """
        Convert markdown to Google Docs format and insert into document

        This is a simplified converter that handles:
        - Headers (# ## ###)
        - Bold (**text**)
        - Italic (*text*)
        - Lists (- item)
        - Code blocks (```)

        Args:
            document_id: The document ID
            markdown_content: Markdown content to convert
        """
        try:
            # First, insert all the text
            # Remove markdown formatting for plain text insertion
            plain_text = self._markdown_to_plain_text(markdown_content)
            self.insert_text(document_id, plain_text, 1)

            # Then apply formatting
            requests = self._generate_formatting_requests(markdown_content)

            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': requests}
                ).execute()

            print(f"✅ Content uploaded to Google Doc")

        except HttpError as error:
            print(f"❌ Error converting markdown to Google Docs: {error}")
            raise

    def _markdown_to_plain_text(self, markdown: str) -> str:
        """Convert markdown to plain text, preserving structure"""
        # Remove code block markers
        text = re.sub(r'```[a-z]*\n', '', markdown)
        text = re.sub(r'```', '', text)

        # Keep the actual markdown symbols for now, we'll format them later
        return text

    def _generate_formatting_requests(self, markdown: str) -> list:
        """
        Generate Google Docs API requests for formatting based on markdown

        This is a basic implementation. For production, consider using
        a proper markdown parser.
        """
        requests = []

        # Split into lines
        lines = markdown.split('\n')
        current_index = 1

        for line in lines:
            line_length = len(line) + 1  # +1 for newline

            # Headers
            if line.startswith('# '):
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': current_index,
                            'endIndex': current_index + line_length - 1
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_1'
                        },
                        'fields': 'namedStyleType'
                    }
                })
            elif line.startswith('## '):
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': current_index,
                            'endIndex': current_index + line_length - 1
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_2'
                        },
                        'fields': 'namedStyleType'
                    }
                })
            elif line.startswith('### '):
                requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': current_index,
                            'endIndex': current_index + line_length - 1
                        },
                        'paragraphStyle': {
                            'namedStyleType': 'HEADING_3'
                        },
                        'fields': 'namedStyleType'
                    }
                })

            current_index += line_length

        return requests

    def upload_markdown_document(self, title: str, markdown_content: str) -> tuple[str, str]:
        """
        Create a new Google Doc and upload markdown content

        Args:
            title: Document title
            markdown_content: Markdown content to upload

        Returns:
            Tuple of (document_id, document_url)
        """
        print(f"\n{'='*80}")
        print(f"📤 Uploading to Google Docs: {title}")
        print(f"{'='*80}\n")

        # Create document
        doc_id = self.create_document(title)

        # Upload content
        self.markdown_to_google_docs(doc_id, markdown_content)

        # Get shareable URL
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

        print(f"\n{'='*80}")
        print(f"✅ Document uploaded successfully!")
        print(f"{'='*80}")
        print(f"📄 Title: {title}")
        print(f"🔗 URL: {doc_url}")
        print(f"{'='*80}\n")

        return doc_id, doc_url

    def share_document(
        self,
        document_id: str,
        email: Optional[str] = None,
        role: str = 'writer',
        make_public: bool = False
    ):
        """
        Share a document with a user or make it public

        Args:
            document_id: The document ID
            email: Email address to share with (optional if make_public=True)
            role: Access role ('reader', 'writer', 'owner')
            make_public: If True, make the document publicly accessible
        """
        try:
            if make_public:
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                self.drive_service.permissions().create(
                    fileId=document_id,
                    body=permission
                ).execute()
                print(f"✅ Document is now publicly accessible")

            elif email:
                permission = {
                    'type': 'user',
                    'role': role,
                    'emailAddress': email
                }
                self.drive_service.permissions().create(
                    fileId=document_id,
                    body=permission,
                    sendNotificationEmail=True
                ).execute()
                print(f"✅ Document shared with {email} as {role}")

        except HttpError as error:
            print(f"❌ Error sharing document: {error}")
            raise

    def move_to_folder(self, document_id: str, folder_id: str):
        """
        Move a document to a specific folder

        Args:
            document_id: The document ID
            folder_id: The folder ID to move to
        """
        try:
            # Retrieve the existing parents to remove
            file = self.drive_service.files().get(
                fileId=document_id,
                fields='parents'
            ).execute()

            previous_parents = ",".join(file.get('parents', []))

            # Move the file to the new folder
            self.drive_service.files().update(
                fileId=document_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

            print(f"✅ Document moved to folder {folder_id}")

        except HttpError as error:
            print(f"❌ Error moving document: {error}")
            raise

    def export_as_pdf(self, document_id: str, output_path: str):
        """
        Export a Google Doc as PDF

        Args:
            document_id: The document ID
            output_path: Local path to save the PDF
        """
        try:
            # Export as PDF
            request = self.drive_service.files().export_media(
                fileId=document_id,
                mimeType='application/pdf'
            )

            import io
            from googleapiclient.http import MediaIoBaseDownload

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()

            # Save to file
            with open(output_path, 'wb') as f:
                f.write(fh.getvalue())

            print(f"✅ PDF exported to: {output_path}")

        except HttpError as error:
            print(f"❌ Error exporting PDF: {error}")
            raise


def setup_google_credentials():
    """
    Helper function to guide users through setting up Google credentials

    This prints instructions for creating a service account and downloading credentials.
    """
    instructions = """
    ╔════════════════════════════════════════════════════════════════╗
    ║         Google Cloud Service Account Setup Instructions        ║
    ╚════════════════════════════════════════════════════════════════╝

    To use Google Docs API, you need to create a service account:

    1. Go to Google Cloud Console:
       https://console.cloud.google.com/

    2. Create a new project or select an existing one

    3. Enable required APIs:
       - Google Docs API
       - Google Drive API

    4. Create a Service Account:
       - Go to "IAM & Admin" > "Service Accounts"
       - Click "Create Service Account"
       - Give it a name and description
       - Grant it the role "Editor" or "Owner"

    5. Create and download a JSON key:
       - Click on the service account you created
       - Go to "Keys" tab
       - Click "Add Key" > "Create new key"
       - Choose "JSON" format
       - Save the downloaded file securely

    6. Set the environment variable:
       export GOOGLE_CREDENTIALS_PATH=/path/to/your/credentials.json

    7. (Optional) Share your Google Drive folder with the service account email
       to allow it to create documents in that folder.

    ════════════════════════════════════════════════════════════════
    """
    print(instructions)
