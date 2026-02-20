"""
app/api/routes/alerts.py — User alert preference management.

Users configure thresholds here. The alert system (Kafka consumer + SendGrid)
reads these preferences when deciding whether to email a user about an edge.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import get_current_user_id
from app.db.session import get_db

router = APIRouter()


class AlertPreferencesUpdate(BaseModel):
    alert_threshold: float | None = None    # Minimum edge magnitude (0.0–1.0)
    alerts_enabled: bool | None = None
    alert_platforms: list[str] | None = None  # ["kalshi", "polymarket"]


@router.get("/preferences")
async def get_alert_preferences(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Return the current user's alert preferences.
    TODO: SELECT from users WHERE auth0_id = user_id.
    """
    return {"user_id": user_id, "preferences": "TODO"}


@router.patch("/preferences")
async def update_alert_preferences(
    body: AlertPreferencesUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the current user's alert preferences.
    TODO: UPSERT into users table.
    """
    return {"user_id": user_id, "updated": body.model_dump(exclude_none=True)}
