"""Federal Register API ingestion."""

from __future__ import annotations

import requests

from project_big_data.logging_setup import get_logger
from project_big_data.policy.ingestion._io import save_raw_json

log = get_logger(__name__)
BASE_URL = "https://www.federalregister.gov/api/v1/documents.json"


def fetch_federal_register(per_page: int = 100) -> dict:
    log.info("Fetching Federal Register documents (per_page=%d)", per_page)
    resp = requests.get(BASE_URL, params={"per_page": per_page}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    data = fetch_federal_register(per_page=100)
    path = save_raw_json(data, prefix="federal_registry")
    log.info("Saved %d documents to %s", len(data.get("results", [])), path)


if __name__ == "__main__":
    main()
