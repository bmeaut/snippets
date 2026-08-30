import os
import datetime
import requests
from icalendar import Calendar
from fastmcp import FastMCP
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Initialize FastMCP Server
mcp = FastMCP("Smart_Student_Calendar")

# Neptun Configuration
NEPTUN_ICS_URL = "[[ICS file weblink]]"

# Google Calendar Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_google_calendar_service():
    """Handles Google OAuth2 authentication."""
    # Get the directory where THIS script is located
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')
    CREDS_PATH = os.path.join(BASE_DIR, 'credentials.json')

    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            
    return build('calendar', 'v3', credentials=creds)

@mcp.tool()
def get_neptun_schedule(days_ahead: int = 7) -> str:
    """Fetches read-only academic schedule from BME Neptun."""
    try:
        response = requests.get(NEPTUN_ICS_URL, timeout=10)
        response.raise_for_status()
        cal = Calendar.from_ical(response.content)
        
        now = datetime.datetime.now(datetime.timezone.utc)
        future_limit = now + datetime.timedelta(days=days_ahead)
        
        events = []
        for component in cal.walk('VEVENT'):
            dtstart = component.get('dtstart')
            if not dtstart: continue
            
            start_time = dtstart.dt
            if not isinstance(start_time, datetime.datetime):
                start_time = datetime.datetime.combine(start_time, datetime.time.min, tzinfo=datetime.timezone.utc)
            elif start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=datetime.timezone.utc)

            if now <= start_time <= future_limit:
                events.append({
                    "summary": str(component.get('summary', 'Class')),
                    "start": start_time.strftime("%Y-%m-%d %H:%M UTC")
                })
        
        events.sort(key=lambda x: x["start"])
        if not events:
            return "No classes scheduled in Neptun."
            
        output = ["Neptun Schedule:"]
        for e in events:
            output.append(f"- {e['start']}: {e['summary']}")
        return "\n".join(output)
        
    except Exception as e:
        return f"Neptun error: {str(e)}"

@mcp.tool()
def get_google_events(days_ahead: int = 7) -> str:
    """Fetches upcoming events from your personal Google Calendar."""
    try:
        service = get_google_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        future_limit = (datetime.datetime.utcnow() + datetime.timedelta(days=days_ahead)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary', timeMin=now, timeMax=future_limit,
            singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return 'No upcoming personal events found.'

        output = ["Google Calendar Events:"]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            output.append(f"- {start}: {event['summary']}")
        return "\n".join(output)

    except Exception as e:
        return f"Google Calendar error: {str(e)}"

@mcp.tool()
def create_personal_event(summary: str, start_time_iso: str, end_time_iso: str, description: str = "") -> str:
    """
    Creates a new event in your Google Calendar.
    Requires ISO format datetime strings (e.g., '2026-08-08T14:00:00+02:00' for Budapest).
    """
    try:
        service = get_google_calendar_service()
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time_iso, 'timeZone': 'Europe/Budapest'},
            'end': {'dateTime': end_time_iso, 'timeZone': 'Europe/Budapest'},
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created successfully! Link: {event.get('htmlLink')}"
        
    except Exception as e:
        return f"Failed to create event: {str(e)}"

if __name__ == "__main__":
    mcp.run()
