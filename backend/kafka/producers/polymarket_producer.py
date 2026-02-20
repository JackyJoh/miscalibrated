"""
kafka/producers/polymarket_producer.py — Polls Polymarket CLOB API and publishes to Kafka.

Polymarket is more complex than Kalshi because it's a decentralized,
web3-based platform. Key differences:
  - Uses a CLOB (Central Limit Order Book) API via their Gamma Markets infrastructure
  - Market IDs are Ethereum token addresses (condition IDs)
  - Prices are expressed per-outcome token (0.0 to 1.0)
  - Their REST CLOB API doesn't require authentication for reads

TODO: Polymarket also has a WebSocket stream for real-time order book updates.
      Consider switching from REST polling to WebSocket in V2 for lower latency.

Usage:
    python -m kafka.producers.polymarket_producer
"""

import json
import logging
import os
import time

import httpx
from confluent_kafka import KafkaException, Producer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [polymarket-producer] %(message)s")
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
POLYMARKET_CLOB_URL     = os.getenv("POLYMARKET_CLOB_URL", "https://clob.polymarket.com")
POLL_INTERVAL_SECONDS   = int(os.getenv("POLYMARKET_POLL_INTERVAL", "60"))

TOPIC = "polymarket.markets"


def delivery_report(err, msg):
    if err:
        log.error(f"Delivery failed for key={msg.key()}: {err}")
    else:
        log.debug(f"Delivered to {msg.topic()} partition={msg.partition()} offset={msg.offset()}")


def create_producer() -> Producer:
    return Producer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "acks": "all",
        "retries": 5,
        "retry.backoff.ms": 500,
    })


def fetch_polymarket_markets(client: httpx.Client) -> list[dict]:
    """
    Fetch active markets from Polymarket's Gamma Markets API.

    Polymarket's Gamma Markets REST API (gamma-api.polymarket.com) gives access
    to market metadata in a simple HTTP/JSON format — no web3 wallet required for reads.

    TODO: Handle pagination (next_cursor field in response).
    TODO: Normalize the yes/no token prices into a single "yes_price" float.
          Polymarket returns token0 and token1 prices; match to outcome label.
    """
    response = client.get(
        "https://gamma-api.polymarket.com/markets",
        params={"active": "true", "closed": "false", "limit": 200},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    # Gamma API returns a list of markets directly (or wrapped — check their docs)
    return data if isinstance(data, list) else data.get("markets", [])


def run():
    """Main polling loop."""
    producer = create_producer()
    log.info(f"Polymarket producer started. Polling every {POLL_INTERVAL_SECONDS}s → topic: {TOPIC}")

    with httpx.Client() as client:
        while True:
            try:
                markets = fetch_polymarket_markets(client)
                log.info(f"Fetched {len(markets)} markets from Polymarket")

                for market in markets:
                    # Polymarket uses "conditionId" or "id" as the market identifier
                    key = str(market.get("conditionId", market.get("id", "unknown"))).encode("utf-8")
                    value = json.dumps(market).encode("utf-8")

                    producer.produce(
                        topic=TOPIC,
                        key=key,
                        value=value,
                        on_delivery=delivery_report,
                    )

                producer.flush(timeout=10)

            except httpx.HTTPStatusError as e:
                log.error(f"Polymarket API error: {e.response.status_code} — {e.response.text}")
            except KafkaException as e:
                log.error(f"Kafka error: {e}")
            except Exception as e:
                log.exception(f"Unexpected error: {e}")

            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
