"""
kafka/producers/news_producer.py — Polls NewsAPI and publishes articles to Kafka.

These articles power the RAG (Retrieval Augmented Generation) system:
  1. This producer fetches news articles
  2. The news_consumer reads them, generates embeddings, stores in pgvector
  3. When the AI agent needs context, it queries pgvector for the top-k
     articles most similar to the user's question or a given market

Usage:
    python -m kafka.producers.news_producer
"""

import json
import logging
import os
import time

import httpx
from confluent_kafka import KafkaException, Producer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [news-producer] %(message)s")
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
NEWS_API_KEY            = os.getenv("NEWS_API_KEY", "")
POLL_INTERVAL_SECONDS   = int(os.getenv("NEWS_POLL_INTERVAL", "300"))  # 5 minutes

TOPIC = "news.feed"

# Keywords to search for — these should cover prediction market categories
# TODO: Make this configurable, or derive dynamically from open market titles
SEARCH_QUERIES = [
    "Federal Reserve interest rates",
    "US election 2025",
    "cryptocurrency bitcoin",
    "sports championship",
    "geopolitics conflict",
]


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
    })


def fetch_articles(client: httpx.Client, query: str) -> list[dict]:
    """
    Fetch recent news articles from NewsAPI for a given search query.
    TODO: Add deduplication (NewsAPI may return the same article for multiple queries).
    TODO: Consider GDELT as an alternative/supplement — it's free with no rate limits.
    """
    response = client.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": 20,
            "language": "en",
            "apiKey": NEWS_API_KEY,
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json().get("articles", [])


def run():
    """Main polling loop."""
    producer = create_producer()
    log.info(f"News producer started. Polling every {POLL_INTERVAL_SECONDS}s → topic: {TOPIC}")

    with httpx.Client() as client:
        while True:
            for query in SEARCH_QUERIES:
                try:
                    articles = fetch_articles(client, query)
                    log.info(f"Query '{query}': {len(articles)} articles")

                    for article in articles:
                        # Use the article URL as the key (unique per article)
                        key = article.get("url", "").encode("utf-8")
                        # Attach the search query as metadata for the consumer
                        article["_search_query"] = query
                        value = json.dumps(article).encode("utf-8")

                        producer.produce(
                            topic=TOPIC,
                            key=key,
                            value=value,
                            on_delivery=delivery_report,
                        )

                    producer.flush(timeout=10)
                    time.sleep(1)  # Brief pause between queries to respect rate limits

                except httpx.HTTPStatusError as e:
                    log.error(f"NewsAPI error for query '{query}': {e.response.status_code}")
                except KafkaException as e:
                    log.error(f"Kafka error: {e}")
                except Exception as e:
                    log.exception(f"Unexpected error for query '{query}': {e}")

            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
