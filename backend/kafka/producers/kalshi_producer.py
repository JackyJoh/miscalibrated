"""
kafka/producers/kalshi_producer.py — Polls Kalshi REST API and publishes market data to Kafka.

HOW KAFKA PRODUCERS WORK (plain English):
──────────────────────────────────────────
A producer is a process that sends ("produces") messages to a Kafka topic.
A topic is like a named, persistent queue. The producer doesn't know or care
who will read its messages — it just writes and moves on.

This script runs on a loop:
  1. Call the Kalshi REST API to get the current list of open markets
  2. For each market, serialize it to JSON
  3. Publish that JSON to the "kalshi.markets" Kafka topic
  4. Sleep for POLL_INTERVAL seconds, then repeat

Run this script as a long-running process (or in Docker, or as a systemd service).
It's completely independent from the FastAPI web server.

Usage:
    python -m kafka.producers.kalshi_producer
"""

import json
import logging
import os
import time

import httpx
from confluent_kafka import Producer, KafkaException

logging.basicConfig(level=logging.INFO, format="%(asctime)s [kalshi-producer] %(message)s")
log = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KALSHI_API_KEY          = os.getenv("KALSHI_API_KEY", "")
KALSHI_BASE_URL         = os.getenv("KALSHI_BASE_URL", "https://trading-api.kalshi.com/trade-api/v2")
POLL_INTERVAL_SECONDS   = int(os.getenv("KALSHI_POLL_INTERVAL", "60"))

# Kafka topic name: all Kalshi market data goes here.
# Consumers subscribe to this topic to receive and process the data.
TOPIC = "kalshi.markets"


def delivery_report(err, msg):
    """
    Callback invoked by the Kafka producer after each message is acknowledged
    by the broker (success) or fails permanently (failure).

    This runs asynchronously — you don't wait for it, Kafka calls it for you.
    """
    if err:
        log.error(f"Delivery failed for key={msg.key()}: {err}")
    else:
        log.debug(f"Delivered to {msg.topic()} partition={msg.partition()} offset={msg.offset()}")


def create_producer() -> Producer:
    """
    Create and return a Kafka Producer instance.

    bootstrap.servers: One or more Kafka broker addresses to connect to.
    acks: "all" means the broker waits for all in-sync replicas to confirm
          before acknowledging — highest durability. Use "1" for local dev speed.
    """
    return Producer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "acks": "all",
        "retries": 5,
        "retry.backoff.ms": 500,
    })


def fetch_kalshi_markets(client: httpx.Client) -> list[dict]:
    """
    Call the Kalshi REST API and return a list of open markets.
    TODO: Implement pagination (Kalshi uses cursor-based pagination).
    TODO: Handle rate limiting (429 responses).
    """
    headers = {"Authorization": f"Token {KALSHI_API_KEY}"}
    response = client.get(
        f"{KALSHI_BASE_URL}/markets",
        headers=headers,
        params={"status": "open", "limit": 200},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    # Kalshi wraps markets in a "markets" key in the response
    return data.get("markets", [])


def run():
    """Main polling loop. Runs indefinitely until interrupted."""
    producer = create_producer()
    log.info(f"Kalshi producer started. Polling every {POLL_INTERVAL_SECONDS}s → topic: {TOPIC}")

    with httpx.Client() as client:
        while True:
            try:
                markets = fetch_kalshi_markets(client)
                log.info(f"Fetched {len(markets)} markets from Kalshi")

                for market in markets:
                    # Use the market's external ticker as the Kafka message key.
                    # Kafka guarantees that messages with the same key go to the
                    # same partition — useful for ordering guarantees per market.
                    key = market.get("ticker", "unknown").encode("utf-8")
                    value = json.dumps(market).encode("utf-8")

                    producer.produce(
                        topic=TOPIC,
                        key=key,
                        value=value,
                        on_delivery=delivery_report,
                    )

                # producer.flush() waits until all queued messages are delivered.
                # Call this periodically — not after every single message — for throughput.
                producer.flush(timeout=10)

            except httpx.HTTPStatusError as e:
                log.error(f"Kalshi API error: {e.response.status_code} — {e.response.text}")
            except KafkaException as e:
                log.error(f"Kafka error: {e}")
            except Exception as e:
                log.exception(f"Unexpected error: {e}")

            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
