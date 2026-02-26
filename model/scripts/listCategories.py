import csv
import time
import requests

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
PAGE_SLEEP = 0.1
OUTPUT_PATH = "data/categories.csv"

_series_cache = {}
_session = requests.Session()


def extract_series_ticker(event_ticker):
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
    series_ticker = extract_series_ticker(event_ticker)
    if not series_ticker:
        return "(none)"
    if series_ticker in _series_cache:
        return _series_cache[series_ticker]
    try:
        resp = _session.get(f"{BASE_URL}/series/{series_ticker}", timeout=10)
        cat = resp.json().get("series", {}).get("category", "(none)") if resp.status_code == 200 else "(none)"
    except Exception:
        cat = "(none)"
    _series_cache[series_ticker] = cat
    return cat


def save(categories, page):
    sorted_cats = sorted(categories.items(), key=lambda x: -x[1])
    print(f"\nPage {page}:")
    for cat, count in sorted_cats:
        print(f"  {count:>6}  {cat}")
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "market_count"])
        writer.writeheader()
        for cat, count in sorted_cats:
            writer.writerow({"category": cat, "market_count": count})
    print(f"  -> saved to {OUTPUT_PATH}")


categories = {}
cursor = None

for page in range(1, 9999):
    params = {"limit": 100}
    if cursor:
        params["cursor"] = cursor

    resp = _session.get(f"{BASE_URL}/historical/markets", params=params, timeout=10)
    if resp.status_code == 429:
        print(f"Rate limited at page {page} — waiting 30s...")
        time.sleep(30)
        continue
    resp.raise_for_status()
    data = resp.json()
    markets = data.get("markets", [])

    if page % 10 == 0:
        for m in markets:
            cat = get_category(m.get("event_ticker", ""))
            categories[cat] = categories.get(cat, 0) + 1

    cursor = data.get("cursor")

    if page % 20 == 0 or not cursor or not markets:
        save(categories, page)

    if not cursor or not markets:
        print(f"Finished at page {page}")
        break

    time.sleep(PAGE_SLEEP)
