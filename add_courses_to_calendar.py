from __future__ import print_function
from datetime import datetime, timedelta
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_service():
    """Authorize and return Google Calendar service (reuses token.json)."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def create_recurring_event(service, summary, location, start_dt, end_dt, calendar_id="primary"):
    """Create a weekly recurring event for 14 weeks."""
    event = {
        "summary": summary,
        "location": location,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Istanbul"},
        "end":   {"dateTime": end_dt.isoformat(),   "timeZone": "Europe/Istanbul"},
        # 14 total occurrences including the first one
        "recurrence": ["RRULE:FREQ=WEEKLY;COUNT=14"],
    }
    created = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"Created: {created.get('summary')} — {created.get('htmlLink')}")

def main():
    service = get_service()

    # Base Monday of the semester (must be a Monday) — 2025-09-29 IS a Monday
    semester_start_monday = datetime(2025, 9, 29)

    # Your weekly timetable
    courses = [
        # Mon
        {"summary": "CENG315/1", "location": "BMB1", "day": "Mon", "start": "08:40", "end": "10:30"},
        # Tue
        {"summary": "CENG477/1", "location": "BMB1", "day": "Tue", "start": "08:40", "end": "10:30"},
        {"summary": "CENG463/1", "location": "BMB4", "day": "Tue", "start": "11:40", "end": "13:30"},
        {"summary": "CENG491/1", "location": "BMB1", "day": "Tue", "start": "13:40", "end": "15:30"},
        # Wed
        {"summary": "CENG477/1", "location": "BMB1", "day": "Wed", "start": "08:40", "end": "10:30"},
        {"summary": "CENG463/1", "location": "BMB4", "day": "Wed", "start": "11:40", "end": "13:30"},
        {"summary": "EE281/2",   "location": "BMB2", "day": "Wed", "start": "13:40", "end": "15:30"},
        {"summary": "CENG489/1", "location": "BMB5", "day": "Wed", "start": "15:40", "end": "17:30"},
        # Thu
        {"summary": "CENG315/1", "location": "BMB1", "day": "Thu", "start": "08:40", "end": "10:30"},
        {"summary": "EE281/2",   "location": "BMB2", "day": "Thu", "start": "15:40", "end": "17:30"},
        # Fri
        {"summary": "CENG489/1", "location": "BMB5", "day": "Fri", "start": "15:40", "end": "17:30"},
    ]

    day_to_offset = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}

    for c in courses:
        # Date of first occurrence for this class
        date0 = semester_start_monday + timedelta(days=day_to_offset[c["day"]])
        sh, sm = map(int, c["start"].split(":"))
        eh, em = map(int, c["end"].split(":"))
        start_dt = date0.replace(hour=sh, minute=sm, second=0, microsecond=0)
        end_dt   = date0.replace(hour=eh, minute=em, second=0, microsecond=0)

        create_recurring_event(
            service,
            summary=c["summary"],
            location=c["location"],
            start_dt=start_dt,
            end_dt=end_dt,
        )

if __name__ == "__main__":
    main()
