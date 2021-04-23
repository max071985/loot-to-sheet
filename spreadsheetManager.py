from singleton import Singleton
from pprint import pprint
from googleapiclient import discovery
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If you modify this, delete token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

class SpreadsheetManager(metaclass=Singleton):
    def __init__(self):
        self._creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self._creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self._creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self._creds.to_json())
        self._service = build('sheets', 'v4', credentials=self._creds)


    def create_Spreadsheet(self, spreadsheet_body = None):
        if spreadsheet_body is None:
            spreadsheet_body = {
                'properties': {
                    'title': Title,
                }
            }
        request = self._service.spreadsheets().create(body=spreadsheet_body)
        response = request.execute()

        pprint(response)
