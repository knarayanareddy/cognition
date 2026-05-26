"""Google Calendar OAuth endpoints (EP-01, EP-02).

EP-01: POST /api/v1/auth/google/init — Initiate Google Calendar OAuth flow
EP-02: GET /api/v1/auth/google/callback — Exchange code for token
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import UserToken

router = APIRouter()

# Google Calendar OAuth scopes — read-only + event creation for INT-01
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

# In-memory state store for OAuth flow (production would use Redis/DB)
_oauth_states: dict[str, dict] = {}


def _create_flow() -> Flow:
    """Create Google OAuth flow from client credentials."""
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uris": [settings.google_redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri,
    )
    return flow


@router.post("/google/init")
async def google_auth_init():
    """EP-01: Initiate Google Calendar OAuth flow.

    Returns auth_url for the frontend to redirect the user to Google consent screen.
    No auth required.
    """
    flow = _create_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    # Store state for verification in callback
    _oauth_states[state] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "auth_url": auth_url,
        "state": state,
    }


@router.get("/google/callback")
async def google_auth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """EP-02: Google Calendar OAuth callback.

    Exchanges authorization code for access token. No auth required.
    """
    # Verify state
    if state not in _oauth_states:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    # Clean up used state
    del _oauth_states[state]

    # Exchange code for token
    flow = _create_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials

    # Generate a user_id (in production, derive from Google profile)
    user_id = uuid.uuid4()

    # Store token securely
    user_token = UserToken(
        user_id=user_id,
        google_access_token=credentials.token,
        google_refresh_token=credentials.refresh_token,
        token_expiry=credentials.expiry.replace(tzinfo=timezone.utc) if credentials.expiry else None,
    )

    # Upsert token
    existing = db.query(UserToken).filter(UserToken.user_id == user_id).first()
    if existing:
        existing.google_access_token = credentials.token
        existing.google_refresh_token = credentials.refresh_token or existing.google_refresh_token
        existing.token_expiry = user_token.token_expiry
    else:
        db.add(user_token)

    db.commit()

    return {
        "user_id": str(user_id),
        "access_token": credentials.token,
        "consent_granted": True,
    }
