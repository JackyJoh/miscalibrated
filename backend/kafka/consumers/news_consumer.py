"""
kafka/consumers/news_consumer.py — Reads news articles from Kafka, generates
embeddings, and stores them in PostgreSQL via pgvector.

HOW RAG (Retrieval Augmented Generation) WORKS HERE:
──────────────────────────────────────────────────────
1. This consumer reads articles from the "news.feed" topic
2. For each article, it:
   a. Chunks the article content into ~500 token segments
   b. Calls an embedding model (e.g. text-embedding-3-small) to convert
      each chunk into a 1536-dimensional float vector
   c. Stores the chunk + vector in the "article_chunks" table in PostgreSQL
3. When the AI agent needs context for a question, it:
   a. Embeds the question with the same embedding model
   b. Queries pgvector for the top-k most similar chunks
      (similarity = cosine distance between vectors)
   c. Passes those chunks as context to the LLM prompt

This is the standard RAG pattern — it lets the LLM "remember" recent news
without exceeding its context window or requiring fine-tuning.

Usage:
    python -m kafka.consumers.news_consumer
"""

import json
import logging
import os
import signal

from confluent_kafka import Consumer, KafkaError, KafkaException

logging.basicConfig(level=logging.INFO, format="%(asctime)s [news-consumer] %(message)s")
log = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
DATABASE_URL            = os.getenv("DATABASE_URL", "postgresql://miscalibrated:devpassword@localhost:5432/miscalibrated")
ANTHROPIC_API_KEY       = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY          = os.getenv("OPENAI_API_KEY", "")

TOPIC    = "news.feed"
GROUP_ID = "news-consumer"

# Max characters per chunk before embedding. ~500 tokens ≈ 2000 chars.
CHUNK_SIZE = 2000

running = True


def handle_signal(sig, frame):
    global running
    log.info("Shutdown signal received — finishing current batch...")
    running = False


def create_consumer() -> Consumer:
    return Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Split text into overlapping chunks for embedding.
    Overlap (200 chars) prevents losing context at chunk boundaries.
    TODO: Use a proper token-aware chunker (e.g. tiktoken) for accuracy.
    """
    overlap = 200
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def embed_text(text: str) -> list[float] | None:
    """
    Convert text to a vector embedding using OpenAI's embedding model.

    We use OpenAI's text-embedding-3-small here because it's fast, cheap,
    and produces 1536-dimensional vectors that work well with pgvector.

    TODO: Add Anthropic embedding support if/when they release an embedding API.
    TODO: Batch multiple chunks in a single API call for efficiency.
    """
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        log.error(f"Embedding failed: {e}")
        return None


def store_chunk(article_url: str, chunk_text: str, embedding: list[float], metadata: dict):
    """
    Insert a text chunk and its vector embedding into PostgreSQL.

    The SQL will look like:
        INSERT INTO article_chunks (url, content, embedding, metadata)
        VALUES ($1, $2, $3::vector, $4)
        ON CONFLICT (url, chunk_index) DO NOTHING;

    pgvector stores the embedding as a vector column, enabling:
        SELECT * FROM article_chunks
        ORDER BY embedding <=> query_embedding   -- cosine similarity search
        LIMIT 5;

    TODO: Implement using asyncpg with pgvector extension.
    """
    log.debug(f"TODO: store chunk for {article_url[:60]}... dim={len(embedding)}")


def process_article(article: dict):
    """Process a single news article: chunk it, embed each chunk, store all."""
    url     = article.get("url", "")
    title   = article.get("title", "")
    content = article.get("content", "") or article.get("description", "")

    if not content:
        log.debug(f"Skipping article with no content: {url}")
        return

    # Prepend title to each chunk for better retrieval relevance
    full_text = f"{title}\n\n{content}"
    chunks = chunk_text(full_text)

    metadata = {
        "url": url,
        "title": title,
        "published_at": article.get("publishedAt"),
        "source": article.get("source", {}).get("name"),
        "search_query": article.get("_search_query"),
    }

    for chunk in chunks:
        embedding = embed_text(chunk)
        if embedding:
            store_chunk(url, chunk, embedding, metadata)

    log.info(f"Processed article '{title[:50]}' → {len(chunks)} chunks")


def run():
    """Main consumer loop."""
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    consumer = create_consumer()
    consumer.subscribe([TOPIC])
    log.info(f"News consumer subscribed to: {TOPIC}")

    try:
        while running:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    log.debug(f"End of partition: {msg.topic()} [{msg.partition()}]")
                else:
                    raise KafkaException(msg.error())
                continue

            try:
                article = json.loads(msg.value().decode("utf-8"))
                process_article(article)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                log.error(f"Failed to decode message: {e}")

            consumer.commit(message=msg)

    finally:
        consumer.close()
        log.info("News consumer closed cleanly.")


if __name__ == "__main__":
    run()
