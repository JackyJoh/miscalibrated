"""
kafka/consumers/markets_consumer.py — Reads market data from Kafka and writes to PostgreSQL.

HOW KAFKA CONSUMERS WORK (plain English):
──────────────────────────────────────────
A consumer subscribes to one or more Kafka topics and processes messages
in order. Key concepts:

  Consumer Group: A named group of consumer processes. Kafka distributes
    topic partitions across all consumers in a group. If you run two
    instances of this consumer with the same group ID, Kafka splits the
    work between them (horizontal scaling). Here we use group "markets-consumer".

  Offset: Kafka tracks which messages each consumer group has processed
    using an "offset" (an incrementing message number per partition).
    When this process restarts, it picks up from where it left off — no
    messages are missed or re-processed (unless you reset offsets intentionally).

  auto.offset.reset: If this consumer starts with no previously committed
    offset (first run), "earliest" means "start from the beginning of the topic".
    Use "latest" to only process messages arriving after startup.

This consumer:
  1. Subscribes to kalshi.markets and polymarket.markets topics
  2. Receives raw JSON market payloads from the producers
  3. Normalizes them into the shared Market schema
  4. Upserts into the PostgreSQL markets table (insert or update on conflict)

Usage:
    python -m kafka.consumers.markets_consumer
"""

import json
import logging
import os
import signal
import sys

from confluent_kafka import Consumer, KafkaException, KafkaError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [markets-consumer] %(message)s")
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
DATABASE_URL            = os.getenv("DATABASE_URL", "postgresql://miscalibrated:devpassword@localhost:5432/miscalibrated")

# The topics this consumer subscribes to
TOPICS = ["kalshi.markets", "polymarket.markets"]

# Consumer group ID: All instances of this consumer share this ID.
# Kafka tracks the group's offset so messages are never processed twice.
GROUP_ID = "markets-consumer"

# Graceful shutdown flag
running = True


def handle_signal(sig, frame):
    """Catch SIGTERM/SIGINT so we can flush and exit cleanly."""
    global running
    log.info("Shutdown signal received — finishing current batch...")
    running = False


def create_consumer() -> Consumer:
    """
    Create and return a Kafka Consumer.

    enable.auto.commit: We set this to False so we commit offsets manually
      AFTER successfully writing to the DB. If we crash mid-write, the
      message will be re-delivered on next startup (at-least-once delivery).
    """
    return Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,   # Commit offsets manually after DB write
    })


def normalize_kalshi(raw: dict) -> dict | None:
    """
    Transform raw Kalshi API response into the shared Market schema.
    TODO: Map all relevant Kalshi fields. This is a minimal placeholder.
    """
    try:
        return {
            "platform": "kalshi",
            "external_id": raw["ticker"],
            "title": raw.get("title", ""),
            "category": raw.get("category", ""),
            "close_time": raw.get("close_time"),
            # Kalshi yes price is in cents (0–100), normalize to 0–1
            "yes_price": (raw.get("yes_bid", 0) + raw.get("yes_ask", 0)) / 200,
            "volume": raw.get("volume", 0),
            "is_open": raw.get("status") == "open",
        }
    except (KeyError, TypeError) as e:
        log.warning(f"Failed to normalize Kalshi market: {e}")
        return None


def normalize_polymarket(raw: dict) -> dict | None:
    """
    Transform raw Polymarket API response into the shared Market schema.
    TODO: Map Polymarket's outcome tokens to yes_price.
          Polymarket returns token prices as strings ("0.62"), not floats.
    """
    try:
        return {
            "platform": "polymarket",
            "external_id": raw.get("conditionId", raw.get("id", "")),
            "title": raw.get("question", raw.get("title", "")),
            "category": raw.get("category", ""),
            "close_time": raw.get("endDate"),
            "yes_price": float(raw.get("outcomePrices", ["0"])[0]),  # First outcome = YES
            "volume": float(raw.get("volume", 0)),
            "is_open": raw.get("active", False),
        }
    except (KeyError, TypeError, ValueError) as e:
        log.warning(f"Failed to normalize Polymarket market: {e}")
        return None


def upsert_market(normalized: dict):
    """
    Insert or update a market record in PostgreSQL.
    TODO: Implement using asyncpg or SQLAlchemy.
          Use ON CONFLICT (external_id) DO UPDATE SET ... for idempotent upserts.
    """
    log.debug(f"TODO upsert: {normalized['platform']} / {normalized['external_id']}")


def run():
    """Main consumer loop."""
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    consumer = create_consumer()
    consumer.subscribe(TOPICS)
    log.info(f"Markets consumer subscribed to: {TOPICS}")

    try:
        while running:
            # poll() blocks for up to 1 second waiting for a message.
            # Returns None if no message arrived within the timeout.
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue  # No message this poll cycle

            if msg.error():
                # PARTITION_EOF is normal — it just means we've caught up
                # to the end of a partition. Not an actual error.
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    log.debug(f"End of partition: {msg.topic()} [{msg.partition()}]")
                else:
                    raise KafkaException(msg.error())
                continue

            # Determine which platform this message came from by topic name
            topic = msg.topic()
            try:
                raw = json.loads(msg.value().decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                log.error(f"Failed to decode message from {topic}: {e}")
                consumer.commit(message=msg)  # Skip bad messages
                continue

            # Normalize and write to DB
            if topic == "kalshi.markets":
                normalized = normalize_kalshi(raw)
            elif topic == "polymarket.markets":
                normalized = normalize_polymarket(raw)
            else:
                normalized = None

            if normalized:
                upsert_market(normalized)

            # Commit the offset AFTER successful processing.
            # This guarantees we won't lose the message if we crash before writing.
            consumer.commit(message=msg)

    finally:
        # Always close the consumer on exit — this releases partition assignments
        # back to Kafka so other consumers in the group can take them over.
        consumer.close()
        log.info("Markets consumer closed cleanly.")


if __name__ == "__main__":
    run()
