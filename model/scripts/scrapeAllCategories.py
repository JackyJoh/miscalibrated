"""
Overnight per-category Kalshi scraper.

For every finalized market, fetches daily + hourly candlesticks and writes
one CSV per granularity per category under model/data/.

Public endpoints used (no auth required):
  GET /historical/markets                        — market list
  GET /historical/markets/{ticker}/candlesticks  — OHLC data

Output (run from the model/ directory):
  data/kalshi_{category}_candles_1d.csv
  data/kalshi_{category}_candles_1h.csv
  data/scrape_log_{YYYYMMDD_HHMM}.txt

Flip TEST_MODE = False for the overnight run.
"""

import csv
import os
import time
from datetime import datetime

import requests

# ── Config ──────────────────────────────────────────────────────────────────
TEST_MODE          = False  # flip to True for test run
TEST_DURATION_SECS = 120    # 2 minutes (only used when TEST_MODE = True)
PAGE_SLEEP         = 0.1
CANDLE_SLEEP       = 0.5    # 500ms between candle fetches to stay under rate limit
RETRY_SLEEP        = 30
MIN_MARKET_VOLUME  = 50
MAX_BID_ASK_SPREAD = 0.40   # prices are 0-1 decimals; spread compared directly

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
DATA_DIR = "data"

# ── Logging setup ────────────────────────────────────────────────────────────
os.makedirs(DATA_DIR, exist_ok=True)

log_path = os.path.join(DATA_DIR, f"scrape_log_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
log_file = open(log_path, "w", encoding="utf-8")


def log(msg=""):
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()


# ── Shared session + series cache ────────────────────────────────────────────
_session      = requests.Session()
_series_cache = {}


# ── Helper functions ─────────────────────────────────────────────────────────

def extract_series_ticker(event_ticker):
    """Strip trailing date suffix from event ticker to get series ticker."""
    if not event_ticker:
        return ""
    parts = event_ticker.split("-")
    series_parts = []
    for part in parts:
        if len(part) >= 2 and part[:2].isdigit():
            break
        series_parts.append(part)
    return "-".join(series_parts) if series_parts else parts[0]


def get_category(event_ticker):
    """Cached /series/{ticker} lookup → category string."""
    series_ticker = extract_series_ticker(event_ticker)
    if not series_ticker:
        return "(none)"
    if series_ticker in _series_cache:
        return _series_cache[series_ticker]
    try:
        resp = _session.get(f"{BASE_URL}/series/{series_ticker}", timeout=10)
        cat = (
            resp.json().get("series", {}).get("category", "(none)")
            if resp.status_code == 200
            else "(none)"
        )
    except Exception:
        cat = "(none)"
    _series_cache[series_ticker] = cat
    return cat


def to_unix(ts):
    """ISO string or int → unix timestamp int, or None."""
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return int(ts)
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except Exception:
        return None


def category_slug(cat):
    return cat.lower().replace(" ", "_").replace("/", "_")


def get_with_retry(url, params=None):
    """GET with 429 rate-limit and transient error handling."""
    while True:
        try:
            resp = _session.get(url, params=params, timeout=15)
            if resp.status_code == 429:
                log(f"  [rate-limit] {url} — sleeping {RETRY_SLEEP}s")
                time.sleep(RETRY_SLEEP)
                continue
            return resp
        except requests.RequestException as exc:
            log(f"  [request error] {url}: {exc} — sleeping {RETRY_SLEEP}s")
            time.sleep(RETRY_SLEEP)


# ── CSV schema ───────────────────────────────────────────────────────────────
CANDLE_FIELDS = [
    "ticker", "event_ticker", "title", "category", "result", "expiration_value",
    "market_open_time", "market_close_time", "market_volume", "candle_ts",
    "yes_bid_open", "yes_bid_high", "yes_bid_low", "yes_bid_close",
    "yes_ask_open", "yes_ask_high", "yes_ask_low", "yes_ask_close",
    "price_open", "price_high", "price_low", "price_close",
    "candle_volume", "open_interest",
]

# Dict of open writers keyed by category slug
writers_1d = {}   # slug → {"file": f, "writer": DictWriter}
writers_1h = {}

# Row counters per category
counts_1d = {}
counts_1h = {}


def get_writer(writers, slug, suffix):
    """Lazily open a CSV writer for this slug+suffix; write header once."""
    if slug not in writers:
        path = os.path.join(DATA_DIR, f"kalshi_{slug}_{suffix}.csv")
        f = open(path, "w", newline="", encoding="utf-8")
        w = csv.DictWriter(f, fieldnames=CANDLE_FIELDS)
        w.writeheader()
        writers[slug] = {"file": f, "writer": w}
        log(f"  [new file] {path}")
    return writers[slug]["writer"]


def close_all_writers():
    for d in (writers_1d, writers_1h):
        for entry in d.values():
            entry["file"].close()


# ── Candle quality filter ────────────────────────────────────────────────────

def candle_passes(c):
    """True if candle has non-zero volume, non-null close price, and tight spread."""
    if not float(c.get("volume") or 0):
        return False
    price = c.get("price") or {}
    if price.get("close") is None:
        return False
    yes_bid   = c.get("yes_bid") or {}
    yes_ask   = c.get("yes_ask") or {}
    bid_close = yes_bid.get("close")
    ask_close = yes_ask.get("close")
    if bid_close is None or ask_close is None:
        return False
    # Prices are decimal strings in 0-1 range (e.g. "0.04"); spread compared directly
    spread = float(ask_close) - float(bid_close)
    return spread <= MAX_BID_ASK_SPREAD


# ── Per-market fetch ─────────────────────────────────────────────────────────

def fetch_and_write_candles(market, category, period_interval, writers, counts, suffix):
    ticker   = market["ticker"]
    open_ts  = to_unix(market.get("open_time") or market.get("market_open_time"))
    close_ts = to_unix(
        market.get("close_time") or market.get("expiration_time")
        or market.get("market_close_time")
    )
    if open_ts is None or close_ts is None:
        return

    resp = get_with_retry(
        f"{BASE_URL}/historical/markets/{ticker}/candlesticks",
        {"period_interval": period_interval, "start_ts": open_ts, "end_ts": close_ts},
    )
    if resp.status_code != 200:
        return

    candles = resp.json().get("candlesticks", [])
    slug    = category_slug(category)
    writer  = get_writer(writers, slug, suffix)

    row_base = {
        "ticker":            ticker,
        "event_ticker":      market.get("event_ticker", ""),
        "title":             market.get("title") or market.get("subtitle") or "",
        "category":          category,
        "result":            market.get("result", ""),
        "expiration_value":  market.get("expiration_value") or market.get("settlement_value") or "",
        "market_open_time":  market.get("open_time") or market.get("market_open_time") or "",
        "market_close_time": (
            market.get("close_time") or market.get("expiration_time")
            or market.get("market_close_time") or ""
        ),
        "market_volume": market.get("volume", ""),
    }

    written = 0
    for c in candles:
        if not candle_passes(c):
            continue
        yes_bid = c.get("yes_bid") or {}
        yes_ask = c.get("yes_ask") or {}
        price   = c.get("price") or {}
        writer.writerow({
            **row_base,
            "candle_ts":     c.get("end_period_ts", ""),
            "yes_bid_open":  yes_bid.get("open", ""),
            "yes_bid_high":  yes_bid.get("high", ""),
            "yes_bid_low":   yes_bid.get("low", ""),
            "yes_bid_close": yes_bid.get("close", ""),
            "yes_ask_open":  yes_ask.get("open", ""),
            "yes_ask_high":  yes_ask.get("high", ""),
            "yes_ask_low":   yes_ask.get("low", ""),
            "yes_ask_close": yes_ask.get("close", ""),
            "price_open":    price.get("open", ""),
            "price_high":    price.get("high", ""),
            "price_low":     price.get("low", ""),
            "price_close":   price.get("close", ""),
            "candle_volume": c.get("volume", ""),
            "open_interest": c.get("open_interest", ""),
        })
        written += 1

    counts[slug] = counts.get(slug, 0) + written
    time.sleep(CANDLE_SLEEP)


# ── Main loop ────────────────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log(f"Kalshi scraper started: {datetime.now().isoformat()}")
    if TEST_MODE:
        log(f"TEST_MODE=True  (stops after {TEST_DURATION_SECS}s)")
    else:
        log("Overnight run — no time limit")
    log("=" * 60)

    cursor       = None
    page         = 0
    markets_ok   = 0
    markets_skip = 0
    start_time   = time.time()

    try:
        while True:
            page += 1
            params = {"limit": 100}
            if cursor:
                params["cursor"] = cursor

            resp = get_with_retry(f"{BASE_URL}/historical/markets", params)
            resp.raise_for_status()
            data    = resp.json()
            markets = data.get("markets", [])
            cursor  = data.get("cursor")

            for m in markets:
                volume = m.get("volume") or 0
                result = m.get("result") or ""
                if volume < MIN_MARKET_VOLUME or not result:
                    markets_skip += 1
                    continue

                category = get_category(m.get("event_ticker", ""))
                fetch_and_write_candles(m, category, 1440, writers_1d, counts_1d, "candles_1d")
                fetch_and_write_candles(m, category, 60,   writers_1h, counts_1h, "candles_1h")
                markets_ok += 1

            if page % 25 == 0:
                log(f"\n--- Page {page} ---")
                log(f"  Markets processed: {markets_ok}  skipped: {markets_skip}")
                log(f"  Daily candle rows:  {counts_1d}")
                log(f"  Hourly candle rows: {counts_1h}")

            if not cursor or not markets:
                log(f"\nAll pages exhausted at page {page}.")
                break

            if TEST_MODE and (time.time() - start_time) >= TEST_DURATION_SECS:
                log(f"\nTEST_MODE: {TEST_DURATION_SECS}s elapsed — stopping after page {page}.")
                break

            time.sleep(PAGE_SLEEP)

    finally:
        close_all_writers()
        log("\n" + "=" * 60)
        log(f"Scrape complete: {datetime.now().isoformat()}")
        log(f"  Markets processed: {markets_ok}  skipped: {markets_skip}")
        log(f"  Daily candle rows:  {counts_1d}")
        log(f"  Hourly candle rows: {counts_1h}")
        log("=" * 60)
        log_file.close()


if __name__ == "__main__":
    main()