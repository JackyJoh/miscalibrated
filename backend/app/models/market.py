"""
app/models/market.py — SQLAlchemy ORM model for prediction market data.

This represents a normalized market record written by Kafka consumers
after they receive raw data from the Kalshi or Polymarket producers.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class MarketPlatform(str, enum.Enum):
    KALSHI = "kalshi"
    POLYMARKET = "polymarket"


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Platform identifier ("kalshi" or "polymarket")
    platform: Mapped[MarketPlatform] = mapped_column(Enum(MarketPlatform), nullable=False, index=True)

    # The platform's own ID for this market (used to deduplicate on upsert)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # Human-readable title, e.g. "Will Bitcoin exceed $100k by end of 2025?"
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    # Category tag from the platform (e.g. "Crypto", "Politics", "Sports")
    category: Mapped[str | None] = mapped_column(String(100))

    # Market close timestamp
    close_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # YES contract price — directly implies the market's probability.
    # e.g. 0.62 means the market thinks there's a 62% chance of YES.
    yes_price: Mapped[float | None] = mapped_column(Float)

    # Total volume traded (in USD or contracts, depending on platform)
    volume: Mapped[float | None] = mapped_column(Float)

    # Whether the market is still open for trading
    is_open: Mapped[bool] = mapped_column(default=True)

    # Timestamps managed automatically by the DB
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
