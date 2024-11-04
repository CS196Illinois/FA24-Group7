import os.path
import requests
import msal
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def main():
    # Google API services
    gmail_service = authenticate_gmail()
    calendar_service = authenticate_calendar()
    
    # Process Gmail messages
    gmail_messages = list_gmail_messages(gmail_service)
    for msg in gmail_messages:
        message = get_gmail_message(gmail_service, 'me', msg['id'])
        payload = message['payload']
        headers = payload.get('headers')
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        
        # Event creation logic needs refined
        if 'meeting' in subject.lower():  
            snippet = message.get('snippet')
            start_time = datetime.datetime.now().isoformat()
            end_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
            create_google_calendar_event(calendar_service, subject, snippet, start_time, end_time)

    # Outlook API services
    token = get_outlook_token()
    outlook_messages = list_outlook_messages(token)
    for msg in outlook_messages:
        subject = msg['subject']
        
        # Event creation logic needs refined
        if 'meeting' in subject.lower():  
            snippet = msg['body']['content']
            start_time = datetime.datetime.now().isoformat()
            end_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
            create_google_calendar_event(calendar_service, subject, snippet, start_time, end_time)

# Authenticate and initialize Gmail API
def authenticate_gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    if os.path.exists('token_gmail.json'):
        creds = Credentials.from_authorized_user_file('token_gmail.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_gmail.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# Authenticate and initialize Calendar API
def authenticate_calendar():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    if os.path.exists('token_calendar.json'):
        creds = Credentials.from_authorized_user_file('token_calendar.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_calendar.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

# List Gmail messages
def list_gmail_messages(service, user_id='me', max_results=10):
    results = service.users().messages().list(userId=user_id, labelIds=['INBOX'], maxResults=max_results).execute()
    return results.get('messages', [])

# Get Gmail message details
def get_gmail_message(service, user_id, msg_id):
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    return message

# Create Google Calendar event
def create_google_calendar_event(service, summary, description, start_time, end_time):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Chicago'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Chicago'
        }
    }
    return service.events().insert(calendarId='primary', body=event).execute()

# Get Outlook token
def get_outlook_token():
    # set as environmental variables
    client_id = os.getenv('CLIENT_ID')
    tenant_id = os.getenv('TENANT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    authority = f'https://login.microsoftonline.com/{tenant_id}'
    scope = ['https://graph.microsoft.com/.default']
    app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
    result = app.acquire_token_silent(scope, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=scope)
    if "access_token" in result:
        return result['access_token']
    else:
        raise Exception("Could not obtain access token")

# List Outlook messages
def list_outlook_messages(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Prefer': 'outlook.body-content-type="text"',
    }
    response = requests.get('https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages', headers=headers)
    response.raise_for_status()
    return response.json()['value']

if __name__ == '__main__':
    main()
