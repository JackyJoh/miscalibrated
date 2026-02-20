"""
app/api/routes/edges.py — Endpoints for viewing detected market edges.

An edge is a market where our model's probability estimate significantly
diverges from the market's implied probability, suggesting mispriced odds.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import verify_token
from app.db.session import get_db

router = APIRouter()


@router.get("/")
async def list_edges(
    min_magnitude: float = Query(0.05, description="Minimum edge magnitude (e.g. 0.05 = 5%)"),
    platform: str | None = None,
    direction: str | None = None,   # "YES" or "NO"
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(verify_token),
):
    """
    Return detected edges above the given magnitude threshold.
    TODO: SELECT from edges JOIN markets WHERE edge_magnitude >= min_magnitude.
    """
    return {"edges": [], "total": 0}


@router.get("/{edge_id}")
async def get_edge(
    edge_id: int,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(verify_token),
):
    """
    Return detailed data for a single edge detection event.
    TODO: Implement.
    """
    return {"edge_id": edge_id, "detail": "TODO"}
