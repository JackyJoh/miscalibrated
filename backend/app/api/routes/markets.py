"""
app/api/routes/markets.py — Endpoints for browsing live prediction market data.

All endpoints require a valid Auth0 JWT (via the verify_token dependency).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import verify_token
from app.db.session import get_db

router = APIRouter()


@router.get("/")
async def list_markets(
    platform: str | None = None,           # Filter by "kalshi" or "polymarket"
    category: str | None = None,           # Filter by category tag
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(verify_token),   # Enforces authentication
):
    """
    Return paginated list of open markets, optionally filtered by platform/category.
    TODO: Implement SELECT query against the markets table.
    """
    return {"markets": [], "total": 0, "limit": limit, "offset": offset}


@router.get("/{market_id}")
async def get_market(
    market_id: int,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(verify_token),
):
    """
    Return detailed data for a single market by internal ID.
    TODO: Implement SELECT with JOIN to edges table for recent edge history.
    """
    return {"market_id": market_id, "detail": "TODO"}
