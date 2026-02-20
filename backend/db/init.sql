-- backend/db/init.sql
-- This script runs automatically when the PostgreSQL Docker container starts
-- for the first time (mounted at /docker-entrypoint-initdb.d/).
-- It runs ONCE — subsequent container restarts skip this file.
--
-- What this does:
--   1. Enables the pgvector extension (needed for vector columns + similarity search)
--   2. Creates the initial schema (tables, indexes)
--
-- In production, use Alembic migrations instead of this file.

-- ─── pgvector Extension ──────────────────────────────────────────────────────
-- pgvector adds the VECTOR data type and similarity search operators to PostgreSQL.
-- Without this, you can't store embeddings or run nearest-neighbor queries.
CREATE EXTENSION IF NOT EXISTS vector;

-- ─── Markets Table ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS markets (
    id          SERIAL PRIMARY KEY,
    platform    VARCHAR(20) NOT NULL CHECK (platform IN ('kalshi', 'polymarket')),
    external_id VARCHAR(255) NOT NULL UNIQUE,
    title       VARCHAR(500) NOT NULL,
    category    VARCHAR(100),
    close_time  TIMESTAMPTZ,
    yes_price   FLOAT,           -- Implied probability (0.0–1.0)
    volume      FLOAT,
    is_open     BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_markets_platform ON markets (platform);
CREATE INDEX IF NOT EXISTS idx_markets_is_open ON markets (is_open);
CREATE INDEX IF NOT EXISTS idx_markets_close_time ON markets (close_time);

-- ─── Edges Table ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS edges (
    id                  SERIAL PRIMARY KEY,
    market_id           INTEGER NOT NULL REFERENCES markets(id),
    market_probability  FLOAT NOT NULL,
    model_probability   FLOAT NOT NULL,
    edge_magnitude      FLOAT NOT NULL,    -- model_probability - market_probability
    direction           VARCHAR(3) NOT NULL CHECK (direction IN ('YES', 'NO')),
    alert_sent          BOOLEAN DEFAULT FALSE,
    detected_at         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_edges_market_id ON edges (market_id);
CREATE INDEX IF NOT EXISTS idx_edges_edge_magnitude ON edges (edge_magnitude DESC);
CREATE INDEX IF NOT EXISTS idx_edges_detected_at ON edges (detected_at DESC);

-- ─── Users Table ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id               SERIAL PRIMARY KEY,
    auth0_id         VARCHAR(255) NOT NULL UNIQUE,  -- "sub" from Auth0 JWT
    email            VARCHAR(255),
    alert_threshold  FLOAT DEFAULT 0.05,            -- Minimum edge to alert on
    alerts_enabled   BOOLEAN DEFAULT TRUE,
    alert_platforms  VARCHAR(50) DEFAULT 'kalshi,polymarket',
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON users (auth0_id);

-- ─── Article Chunks Table (for RAG / pgvector) ───────────────────────────────
-- Stores chunked news article text + vector embeddings.
-- The embedding column uses pgvector's VECTOR type with 1536 dimensions
-- (matches OpenAI text-embedding-3-small output size).
CREATE TABLE IF NOT EXISTS article_chunks (
    id           SERIAL PRIMARY KEY,
    url          TEXT NOT NULL,
    chunk_index  INTEGER NOT NULL,
    content      TEXT NOT NULL,
    -- VECTOR(1536): each embedding is a list of 1536 floats
    -- pgvector stores this efficiently and enables fast similarity search
    embedding    VECTOR(1536),
    source_name  VARCHAR(255),
    published_at TIMESTAMPTZ,
    search_query VARCHAR(255),
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (url, chunk_index)
);

-- IVFFlat index for fast approximate nearest-neighbor search.
-- "lists" controls the number of clusters; ~sqrt(row_count) is a good starting point.
-- This makes similarity queries fast once you have many rows.
-- Note: Build this index AFTER loading a significant amount of data.
-- CREATE INDEX ON article_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
