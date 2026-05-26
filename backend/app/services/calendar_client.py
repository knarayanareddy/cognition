"""Google Calendar API client for LIVE data source (SRC-01).

This is the ONLY live data source. All calendar operations use real OAuth tokens.
Provides:
- Reading calendar events for signal extraction (T-01 through T-07)
- Creating focus block events for INT-01 (the only LIVE intervention)
"""

from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.config import settings


class CalendarClient:
    """Google Calendar API client for CLB signal extraction and INT-01 execution."""

    def __init__(self, access_token: str, refresh_token: str = None):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
        )
        self.service = build("calendar", "v3", credentials=self.credentials)

    def get_todays_events(self) -> list[dict]:
        """Fetch all calendar events for today.

        Used to compute temporal signals T-01 through T-07.
        Returns derived data only (start, end, duration) — never event titles
        or attendee names (privacy: Data Minimisation principle).
        """
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        events_result = self.service.events().list(
            calendarId="primary",
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])

        # Return only derived signals — never raw content (F-07 privacy rules)
        return [
            {
                "start": event.get("start", {}).get("dateTime"),
                "end": event.get("end", {}).get("dateTime"),
                "duration_minutes": self._calculate_duration(event),
                "is_all_day": "date" in event.get("start", {}),
            }
            for event in events
            if event.get("start", {}).get("dateTime")  # Skip all-day events
        ]

    def get_week_events(self, days_back: int = 7) -> list[dict]:
        """Fetch events for the past N days (for T-07: days_without_break)."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days_back)

        events_result = self.service.events().list(
            calendarId="primary",
            timeMin=start.isoformat(),
            timeMax=now.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])

        return [
            {
                "start": event.get("start", {}).get("dateTime"),
                "end": event.get("end", {}).get("dateTime"),
                "duration_minutes": self._calculate_duration(event),
                "date": event.get("start", {}).get("dateTime", "")[:10],
            }
            for event in events
            if event.get("start", {}).get("dateTime")
        ]

    def create_focus_block(self) -> dict:
        """INT-01: Create a focus block event in Google Calendar (LIVE intervention).

        Creates a 2h event titled "Focus Time — CLB Protected".
        Duration controlled by CFG-10 (default: 120 mins).

        This is the ONLY intervention that executes for real.
        """
        now = datetime.now(timezone.utc)
        # Find next available slot (start from next hour)
        start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=settings.focus_block_duration_mins)

        event = {
            "summary": "Focus Time — CLB Protected",
            "description": (
                "This focus block was automatically created by the Cognitive Load Balancer "
                "to protect your deep work time. Your CL score indicated you need "
                "uninterrupted focus time."
            ),
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": settings.timezone,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": settings.timezone,
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 5},
                ],
            },
            "colorId": "2",  # Green — matches LIVE+success colour rule
        }

        created_event = self.service.events().insert(
            calendarId="primary",
            body=event,
        ).execute()

        return {
            "event_id": created_event.get("id"),
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "duration_mins": settings.focus_block_duration_mins,
            "link": created_event.get("htmlLink"),
        }

    @staticmethod
    def _calculate_duration(event: dict) -> int:
        """Calculate event duration in minutes from start/end times."""
        start_str = event.get("start", {}).get("dateTime")
        end_str = event.get("end", {}).get("dateTime")

        if not start_str or not end_str:
            return 0

        start = datetime.fromisoformat(start_str)
        end = datetime.fromisoformat(end_str)
        return int((end - start).total_seconds() / 60)
