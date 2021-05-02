from singleton import Singleton
from pprint import pprint
from googleapiclient import discovery
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If you modify this, delete token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class SpreadsheetManager(metaclass=Singleton):
    """Manage spreadsheet interaction

    Args:
        metaclass : Singleton class. Defaults to Singleton.
    """

    def __init__(self, spreadsheet_id):
        self._id = spreadsheet_id
        self._creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        try:
            if os.path.exists("token.json"):
                self._creds = Credentials.from_authorized_user_file(
                    "token.json", SCOPES
                )
            # If there are no (valid) credentials available, let the user log in.
            if not self._creds or not self._creds.valid:
                if self._creds and self._creds.expired and self._creds.refresh_token:
                    self._creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", SCOPES
                    )
                    self._creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open("token.json", "w") as token:
                    token.write(self._creds.to_json())
                self._service = build("sheets", "v4", credentials=self._creds)
        except Exception as e:
            print(e)
        else:
            print("Successfully connected to Spreadsheets")

    def getData(self, ranges, value_render_option=None, dateTime_render_option=None):
        """Get sheet values from the spreadsheet

        Args:
            ranges ([str]): [Table to get values from (e.g: ranges["a1:a3", "b1:b2"])]
            value_render_option ([type], optional): [idk really]. Defaults to None.
            dateTime_render_option ([type], optional): [idk really]. Defaults to None.
        """
        self._service = build("sheets", "v4", credentials=self._creds)
        try:
            request = (
                self._service.spreadsheets()
                .values()
                .batchGet(
                    spreadsheetId=self._id,
                    ranges=ranges,
                    valueRenderOption=value_render_option,
                    dateTimeRenderOption=dateTime_render_option,
                )
            )
            response = request.execute()
        except Exception as e:
            print(f"Failed to get values. error: \n{e}")
        else:
            print("Successfully gathered the data:")
            pprint(response)
