"""EP-17: DELETE /api/v1/user/data — Delete all user data (GDPR Art. 17 compliant).

Privacy rules (F-07):
- One-click data deletion
- Removes all scores, interventions, and signal snapshots
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CLScore, Intervention, SignalSnapshot, UserConsent, UserToken

router = APIRouter()


class DeleteConfirmation(BaseModel):
    confirm: bool


def get_current_user_id() -> uuid.UUID:
    """Placeholder: returns a fixed user_id for development."""
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.delete("/data")
async def delete_user_data(
    body: DeleteConfirmation,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-17: Delete all user data (GDPR Art. 17 erasure).

    Requires explicit confirmation. Removes all scores, interventions,
    signal snapshots, consent records, and tokens.
    """
    if not body.confirm:
        raise HTTPException(
            status_code=400,
            detail="Deletion requires confirm: true",
        )

    # Count records before deletion
    scores_count = db.query(CLScore).filter(CLScore.user_id == user_id).count()
    interventions_count = db.query(Intervention).filter(Intervention.user_id == user_id).count()
    signals_count = db.query(SignalSnapshot).filter(SignalSnapshot.user_id == user_id).count()

    # Delete all user data
    db.query(CLScore).filter(CLScore.user_id == user_id).delete()
    db.query(Intervention).filter(Intervention.user_id == user_id).delete()
    db.query(SignalSnapshot).filter(SignalSnapshot.user_id == user_id).delete()
    db.query(UserConsent).filter(UserConsent.user_id == user_id).delete()
    db.query(UserToken).filter(UserToken.user_id == user_id).delete()

    db.commit()

    return {
        "user_id": str(user_id),
        "deleted_at": datetime.now(timezone.utc).isoformat(),
        "records_removed": {
            "scores": scores_count,
            "interventions": interventions_count,
            "signals": signals_count,
        },
    }
