import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# GLOBAL CONFIG VALUES
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEETID = "1tVWfI2r6kw1amZbDLhxzBUkK_lPP_u1t0gyV7rZrOY4"
SPREADSHEETRANGE = "engenharia_de_software!A1:H27"

def gsheets_conn():
  creds = None

  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "client_secret.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEETID, range=SPREADSHEETRANGE)
        .execute()
    )
    values = result.get("values", [])
    return values, service
    
  except HttpError as err:
    print(err)

def app():
  spreadsheet_values, service = gsheets_conn()
  print(spreadsheet_values)

app()