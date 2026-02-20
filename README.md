# Miscalibrated — Project Planning Doc

## Concept
A real-time analysis and alert platform for prediction markets (Kalshi & Polymarket). Miscalibrated finds mispriced odds, surfaces actionable insights, and helps users build smarter trading strategies through an embedded AI agent.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite) |
| Backend | FastAPI (Python) |
| Database | PostgreSQL + pgvector |
| Streaming | Apache Kafka |
| Auth | Auth0 |
| Alerts | SendGrid |
| Infrastructure | DigitalOcean |
| LLM | Abstracted service layer (Claude / OpenAI — TBD) |

---

## Architecture Overview

```
Kalshi API ──┐
              ├──► Kafka Producers ──► Kafka Topics ──► Consumers ──► PostgreSQL + pgvector
Polymarket ──┘                                                              │
                                                                            ▼
NewsAPI / GDELT ──► Kafka Producer ──► news.feed topic ──► Chunked + Embedded (pgvector)
                                                                            │
                                                                            ▼
                                                              ML Calibration Model
                                                                            │
                                                                            ▼
                                                              Edge Detection ──► alerts.triggered topic
                                                                                        │
                                                                                        ▼
                                                                                  SendGrid Email
                                                                                        │
                                                                                        ▼
                                                                                 React Dashboard + AI Agent
```

---

## MVP Requirements

### Data Pipeline
- Kafka producers polling Kalshi + Polymarket APIs at regular intervals
- Publishes raw market data to topics: `kalshi.markets`, `polymarket.markets`
- Consumers normalize and write to PostgreSQL
- Kafka acts as event buffer — no data loss if consumer is down

### News Aggregation
- Separate Kafka producer pulling from NewsAPI or GDELT
- Publishes to `news.feed` topic
- Consumer chunks articles, generates embeddings, stores in pgvector
- Articles matched to relevant open markets via keyword/entity matching

### ML Calibration Engine
- Scheduled Python job reads from PostgreSQL
- Computes model-implied probability vs market-implied probability
- Flags edges above configurable threshold
- Writes to `edges` table in PostgreSQL

### Alert System
- Edge detection triggers events on `alerts.triggered` Kafka topic
- Consumer picks up and sends email via SendGrid
- Users can configure alert thresholds (e.g. "notify me when edge > 5%")

### AI Agent
- Embedded in React dashboard as a chat interface
- Has access to tools: query live markets, query edges table, retrieve news via RAG, run quick calibration estimates
- RAG pipeline pulls relevant news chunks from pgvector based on user query
- LLM provider abstracted behind a service layer (swap Claude/OpenAI without touching other code)
- FastAPI endpoint handles agent sessions, streams responses to frontend

### Auth & User Accounts
- Auth0 handles login/signup
- FastAPI validates Auth0 JWT tokens on protected routes
- User preferences and alert settings stored in PostgreSQL, linked via Auth0 user ID

### Frontend Dashboard
- Live market feed (Kalshi + Polymarket)
- Edge detection view — markets with significant mispricing flagged
- Per-market analysis view with news context
- Historical trade analysis
- Alert preferences / settings
- Embedded AI agent chat

---

## Infrastructure (DigitalOcean — $200 credits)

| Service | Purpose |
|---|---|
| Droplet #1 | Kafka + Zookeeper |
| Droplet #2 | FastAPI backend |
| Managed PostgreSQL | DB (use DO managed, not self-hosted) |
| App Platform or Droplet #3 | React frontend |

---

## True MVP (Minimum to be useful)
- Pull live markets from Kalshi + Polymarket
- Detect and display edges (mispriced odds)
- Send email alert when edge is found
- Basic React dashboard to view markets and edges
- User login via Auth0

---

## Nice to Haves
- AI agent strategy builder
- RAG-powered news context per market
- Historical trade analysis
- User-configurable alert thresholds
- Mobile-friendly UI

---

## Expansion / V2
- Auto trade execution (Kalshi + Polymarket APIs support this)
- Additional platforms (Manifold, PredictIt, etc.)
- Advanced ML models (beyond baseline calibration)
- Portfolio tracking
- Social features (share strategies, leaderboards)

---

## Key Implementation Notes

- **Polymarket complexity**: Uses a CLOB API via Gamma Markets (web3-based), slightly more complex than Kalshi's REST API — account for extra integration effort
- **pgvector**: Keeps vector storage inside PostgreSQL, no need for a separate Pinecone/Weaviate instance
- **LLM abstraction**: Wrap all LLM calls in a `LLMService` class so the provider can be swapped without touching agent logic
- **Kafka over scheduler**: Kafka handles event streaming and buffering — no need for Celery/Redis or APScheduler
