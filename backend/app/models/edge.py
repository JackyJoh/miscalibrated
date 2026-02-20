"""
app/models/edge.py — SQLAlchemy ORM model for detected market edges.

An "edge" is when the calibration model's probability estimate diverges
significantly from the market's implied probability (the yes_price).

Example:
  Market: "Will Fed cut rates in July?" → yes_price = 0.45 (market says 45%)
  Our model: estimates 0.62 (62% chance based on news + historical data)
  Edge = 0.62 - 0.45 = 0.17 (17% edge → alert the user)
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Edge(Base):
    __tablename__ = "edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The market this edge was detected on
    market_id: Mapped[int] = mapped_column(Integer, ForeignKey("markets.id"), nullable=False, index=True)
    market: Mapped["Market"] = relationship("Market")  # noqa: F821

    # The market's implied probability at the time of detection
    market_probability: Mapped[float] = mapped_column(Float, nullable=False)

    # Our model's estimated probability
    model_probability: Mapped[float] = mapped_column(Float, nullable=False)

    # The edge magnitude: model_probability - market_probability
    # Positive = market undervaluing YES; negative = market overvaluing YES
    edge_magnitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    # Direction of the edge ("YES" means bet YES, "NO" means bet NO)
    direction: Mapped[str] = mapped_column(String(3), nullable=False)

    # Whether an alert has been sent to eligible users for this edge
    alert_sent: Mapped[bool] = mapped_column(default=False)

    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
