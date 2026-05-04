"""Congress.gov bills API ingestion."""

from __future__ import annotations

import requests

from project_big_data.config import CONGRESS_API_KEY
from project_big_data.logging_setup import get_logger
from project_big_data.policy.ingestion._io import save_raw_json

log = get_logger(__name__)
BASE_URL = "https://api.congress.gov/v3/bill"


def fetch_congress_bills(limit: int = 100) -> dict:
    if not CONGRESS_API_KEY:
        raise RuntimeError("CONGRESS_API_KEY not set in environment.")
    log.info("Fetching Congress bills (limit=%d)", limit)
    resp = requests.get(
        BASE_URL,
        params={"api_key": CONGRESS_API_KEY, "limit": limit, "format": "json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    data = fetch_congress_bills(limit=100)
    path = save_raw_json(data, prefix="congress_bills")
    log.info("Saved %d bills to %s", len(data.get("bills", [])), path)


if __name__ == "__main__":
    main()
