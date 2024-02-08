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

def save_user_data(sheet, data):
    sheet.values().update(
      spreadsheetId=SPREADSHEETID, 
      range=SPREADSHEETRANGE,
      valueInputOption="RAW",
      body={"values": data}).execute()

def resolve_user_data(data):
    total_lessons = int(re.findall(r'\d+', data[1][0])[0])
    
    for i, student in enumerate(data[3:], start=3):
        lessons_taken = int(student[2])
        mean = (float(student[3]) + int(student[4]) + int(student[5])) / 3
        situation = ''
        naf = 0
        if mean >= 70:
            situation = 'Aprovado'
        elif 50 <= mean < 70:
            situation = 'Exame Final'
            naf = 100 - mean
        elif mean < 50:
            situation = 'Reprovado por Nota'
        if lessons_taken > total_lessons * 0.25:
            naf = 0
            situation = 'Reprovado por Falta'
    
        data[i].extend([situation, "{:.2f}".format(naf)])

    return data

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
    return [values, sheet]
    
  except HttpError as err:
    print(err)

def app():
  spreadsheet_values, service = gsheets_conn()
  resolved_student_scores = resolve_user_data(spreadsheet_values)
  save_user_data(service, resolved_student_scores)

app()