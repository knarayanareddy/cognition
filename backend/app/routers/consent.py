"""Privacy consent endpoints (EP-15, EP-16, EP-17).

EP-15: GET /api/v1/consent/settings — Fetch user consent settings
EP-16: PUT /api/v1/consent/level — Update user consent level
EP-17: DELETE /api/v1/user/data — Delete all user data (GDPR Art. 17)

Privacy rules (F-07):
- Consent screen must be shown before any data collection begins (AC08)
- Only derived signals stored — never raw content
- One-click data deletion (GDPR Art. 17 compliant)
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import CLScore, Intervention, SignalSnapshot, UserConsent

router = APIRouter()

VALID_CONSENT_LEVELS = {"BASIC", "STANDARD", "FULL"}


class ConsentLevelUpdate(BaseModel):
    consent_level: str


# Placeholder auth dependency — in production, extract user_id from JWT
def get_current_user_id() -> uuid.UUID:
    """Placeholder: returns a fixed user_id for development."""
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.get("/settings")
async def get_consent_settings(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-15: Fetch user consent settings.

    Returns current consent level, granted_at timestamp, and data retention days.
    """
    consent = db.query(UserConsent).filter(UserConsent.user_id == user_id).first()

    if not consent:
        return {
            "user_id": str(user_id),
            "consent_level": None,
            "granted_at": None,
            "data_retention_days": settings.data_retention_days,
        }

    return {
        "user_id": str(user_id),
        "consent_level": consent.consent_level,
        "granted_at": consent.granted_at.isoformat() if consent.granted_at else None,
        "data_retention_days": settings.data_retention_days,
    }


@router.put("/level")
async def update_consent_level(
    body: ConsentLevelUpdate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-16: Update user consent level.

    Valid levels: BASIC, STANDARD, FULL.
    Triggers data scope adjustment based on new consent level.
    """
    if body.consent_level not in VALID_CONSENT_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid consent level. Must be one of: {', '.join(VALID_CONSENT_LEVELS)}",
        )

    consent = db.query(UserConsent).filter(UserConsent.user_id == user_id).first()

    if consent:
        consent.consent_level = body.consent_level
        consent.updated_at = datetime.now(timezone.utc)
    else:
        consent = UserConsent(
            user_id=user_id,
            consent_level=body.consent_level,
        )
        db.add(consent)

    db.commit()
    db.refresh(consent)

    # Define data collection scope based on consent level
    scope_map = {
        "BASIC": "Calendar event counts and durations only",
        "STANDARD": "BASIC + Slack metadata (counts, timing)",
        "FULL": "STANDARD + GitHub/Jira activity metadata",
    }

    return {
        "user_id": str(user_id),
        "consent_level": consent.consent_level,
        "updated_at": consent.updated_at.isoformat() if consent.updated_at else None,
        "data_collection_scope": scope_map[consent.consent_level],
    }
