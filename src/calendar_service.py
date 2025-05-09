# /home/ubuntu/client_portal_project/client_portal/src/calendar_service.py
import os
import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https.www.googleapis.com/auth/calendar"]

# Placeholder for where your credentials.json file (downloaded from Google Cloud Console) should be.
# This file should NOT be committed to a public repository.
CREDENTIALS_FILE = "/home/ubuntu/client_portal_project/client_portal/credentials.json"
TOKEN_FILE = "/home/ubuntu/client_portal_project/client_portal/token.json"

def get_calendar_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                # Potentially delete token.json and force re-auth
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                return None # Indicate failure to get service
        else:
            # This part needs to be handled by a web flow in a Flask app
            # For now, this indicates that authentication is needed.
            # The actual flow will be initiated from a route.
            print("Credentials not found or invalid. User needs to authenticate.")
            return None # Indicate that authentication is required
        
        # Save the credentials for the next run if they were refreshed
        if creds and creds.valid:
             with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
    
    if not creds or not creds.valid:
        # This case should ideally be caught by the auth flow initiation
        print("Failed to obtain valid credentials.")
        return None

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"An error occurred building the calendar service: {e}")
        return None

def create_event(service, summary, start_datetime_str, end_datetime_str, description='', attendees=None):
    """Creates an event on the user's primary calendar.
    start_datetime_str and end_datetime_str should be in ISO format, e.g., "2024-05-10T09:00:00-07:00"
    attendees is a list of email strings.
    """
    if not service:
        print("Calendar service not available.")
        return None

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_datetime_str,
            "timeZone": "America/Chicago",  # CST/CDT - be mindful of DST
        },
        "end": {
            "dateTime": end_datetime_str,
            "timeZone": "America/Chicago",
        },
    }
    if attendees:
        event["attendees"] = [{"email": email} for email in attendees]

    try:
        created_event = service.events().insert(calendarId="primary", body=event).execute()
        print(f"Event created: {created_event.get('htmlLink')}")
        return created_event
    except Exception as e:
        print(f"An error occurred creating the event: {e}")
        return None

# Example usage (for testing locally, not directly in Flask app without auth flow):
if __name__ == "__main__":
    # This __main__ block is for local testing and requires credentials.json to be present
    # and the user to go through the console-based OAuth flow if token.json is not present/valid.
    print("Attempting to get calendar service for local test...")
    # Create a dummy credentials.json for this test if it doesn't exist
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"{CREDENTIALS_FILE} not found. Please create it with your Google API credentials for local testing.")
        # Example structure for credentials.json:
        # { "installed": { "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com", 
        #                  "project_id": "YOUR_PROJECT_ID", 
        #                  "auth_uri": "https://accounts.google.com/o/oauth2/auth", 
        #                  "token_uri": "https://oauth2.googleapis.com/token", 
        #                  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", 
        #                  "client_secret": "YOUR_CLIENT_SECRET", 
        #                  "redirect_uris": ["http://localhost:8080/", "urn:ietf:wg:oauth:2.0:oob"] } }
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        # Check if token.json exists and is valid
        local_creds = None
        if os.path.exists(TOKEN_FILE):
            local_creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        if not local_creds or not local_creds.valid:
            if local_creds and local_creds.expired and local_creds.refresh_token:
                try:
                    local_creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}. Please re-authenticate.")
                    local_creds = flow.run_local_server(port=0)
            else:
                print("Running local server for authentication...")
                local_creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "w") as token:
                token.write(local_creds.to_json())
        
        service = build("calendar", "v3", credentials=local_creds)
        if service:
            print("Calendar service obtained successfully for local test.")
            # Test creating an event
            now = datetime.datetime.utcnow()
            start_time = (now + datetime.timedelta(days=1)).isoformat() + "Z" # Tomorrow
            end_time = (now + datetime.timedelta(days=1, hours=1)).isoformat() + "Z"
            # create_event(service, "Test Event from Manus", start_time, end_time, description="This is a test event.")
        else:
            print("Failed to get calendar service for local test.")

