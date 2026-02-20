"""
app/main.py — FastAPI application entry point.

This is where the app is assembled: middleware, CORS, and route registration.
Run locally with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import markets, edges, alerts, agent


# ─── Lifespan ────────────────────────────────────────────────────────────────
# The lifespan context manager runs startup and shutdown logic.
# Use this to open DB connection pools, initialize Kafka clients, etc.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────
    # TODO: Initialize database connection pool
    # TODO: Run Alembic migrations on startup (optional — or use a separate script)
    print("✓ Miscalibrated API starting up")
    yield
    # ── Shutdown ─────────────────────────────────────────────────
    # TODO: Close DB pool, flush any pending Kafka messages
    print("✓ Miscalibrated API shutting down")


# ─── App Instance ────────────────────────────────────────────────────────────
app = FastAPI(
    title="Miscalibrated API",
    description="Real-time prediction market edge detection and alerting.",
    version="0.1.0",
    lifespan=lifespan,
)


# ─── CORS Middleware ─────────────────────────────────────────────────────────
# Allows the React frontend (running on localhost:5173) to make requests
# to this API without being blocked by the browser's same-origin policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routes ──────────────────────────────────────────────────────────────────
# Each router handles one domain area. The prefix groups all its endpoints
# under a common URL path. e.g. markets router handles /api/v1/markets/*
app.include_router(markets.router, prefix="/api/v1/markets", tags=["Markets"])
app.include_router(edges.router,   prefix="/api/v1/edges",   tags=["Edges"])
app.include_router(alerts.router,  prefix="/api/v1/alerts",  tags=["Alerts"])
app.include_router(agent.router,   prefix="/api/v1/agent",   tags=["Agent"])


# ─── Health Check ────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    """Simple liveness probe. Returns 200 when the server is running."""
    return {"status": "ok", "version": "0.1.0"}
