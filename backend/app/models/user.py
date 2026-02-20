"""
app/models/user.py — SQLAlchemy ORM model for user preferences.

Auth0 handles all authentication — we don't store passwords.
We use Auth0's user_id (the "sub" claim from the JWT) as the foreign key
to link our internal user preferences to an Auth0 account.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The Auth0 user ID from the JWT "sub" claim, e.g. "auth0|abc123def456"
    # This is how we link Auth0 identity to our internal user record.
    auth0_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Email stored for convenience (also available from Auth0 token payload)
    email: Mapped[str | None] = mapped_column(String(255))

    # ── Alert Preferences ─────────────────────────────────────────────────
    # Users configure the minimum edge magnitude before they get alerted.
    # e.g. 0.05 = only alert when the edge is > 5%
    alert_threshold: Mapped[float] = mapped_column(Float, default=0.05)
    alerts_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Which platforms to receive alerts for (stored as comma-separated string
    # for simplicity in V1; use a junction table in V2)
    alert_platforms: Mapped[str] = mapped_column(String(50), default="kalshi,polymarket")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
