import json
import requests

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

resp = requests.get(f"{BASE_URL}/historical/markets", params={"limit": 3})
resp.raise_for_status()
markets = resp.json().get("markets", [])

for m in markets:
    print(json.dumps(m, indent=2))
    print("---")
