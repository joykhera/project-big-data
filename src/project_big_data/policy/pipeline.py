"""End-to-end policy pipeline: raw JSON -> processed CSVs -> top opportunities.

Replaces the scattered `__main__` blocks across processors and the
`notebooks/basic_analysis.py` script with one entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from project_big_data.config import PROCESSED_DIR, RAW_DIR
from project_big_data.logging_setup import get_logger
from project_big_data.policy.ingestion._io import load_json, save_csv
from project_big_data.policy.processing.features import apply_all_features
from project_big_data.policy.processing.geography import apply_geography
from project_big_data.policy.processing.scoring import apply_opportunity_score
from project_big_data.policy.processing.tagging import apply_industry_tags

log = get_logger(__name__)

FED_REGISTER_CSV = PROCESSED_DIR / "federal_register_documents.csv"
CONGRESS_CSV = PROCESSED_DIR / "congress_bill_documents.csv"
COMBINED_CSV = PROCESSED_DIR / "combined_data.csv"
TOP_CSV = PROCESSED_DIR / "top_opportunities.csv"


def _latest_raw(prefix: str) -> Path | None:
    matches = sorted(RAW_DIR.glob(f"{prefix}*.json"))
    return matches[-1] if matches else None


def transform_federal_register(documents: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for doc in documents:
        rows.append(
            {
                "document_number": doc.get("document_number"),
                "title": doc.get("title"),
                "type": doc.get("type"),
                "publication_date": doc.get("publication_date"),
                "abstract": doc.get("abstract"),
                "agency_names": ", ".join(
                    a.get("name", "") for a in doc.get("agencies", [])
                ),
                "agencies_full": json.dumps(doc.get("agencies", [])),
                "html_url": doc.get("html_url"),
                "pdf_url": doc.get("pdf_url"),
                "public_inspection_pdf_url": doc.get("public_inspection_pdf_url"),
            }
        )
    return pd.DataFrame(rows)


def transform_congress_bills(bills: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for bill in bills:
        latest = bill.get("latestAction", {}) or {}
        rows.append(
            {
                "document_number": bill.get("number"),
                "title": bill.get("title"),
                "type": bill.get("type"),
                "publication_date": bill.get("updateDate"),
                "abstract": latest.get("text"),
                "agency_names": None,
                "agencies_full": None,
                "html_url": bill.get("url"),
                "pdf_url": None,
                "public_inspection_pdf_url": None,
                "congress": bill.get("congress"),
                "origin_chamber": bill.get("originChamber"),
                "origin_chamber_code": bill.get("originChamberCode"),
                "latest_action_date": latest.get("actionDate"),
                "latest_action_text": latest.get("text"),
            }
        )
    return pd.DataFrame(rows)


def _process(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    df = apply_all_features(df, source_name=source_name)
    df = apply_industry_tags(df)
    df = apply_geography(df)
    df = apply_opportunity_score(df)
    return df


def run_federal_register(raw_path: Path | None = None) -> pd.DataFrame:
    raw_path = raw_path or _latest_raw("federal_registry")
    if raw_path is None:
        raise FileNotFoundError("No federal_registry_*.json in data/raw_data/")
    log.info("Processing federal register from %s", raw_path)
    data = load_json(raw_path)
    df = transform_federal_register(data.get("results", []))
    df = _process(df, source_name="federal_register")
    save_csv(df, FED_REGISTER_CSV)
    return df


def run_congress(raw_path: Path | None = None) -> pd.DataFrame:
    raw_path = raw_path or _latest_raw("congress_bills")
    if raw_path is None:
        raise FileNotFoundError("No congress_bills_*.json in data/raw_data/")
    log.info("Processing congress bills from %s", raw_path)
    data = load_json(raw_path)
    df = transform_congress_bills(data.get("bills", []))
    df = _process(df, source_name="congress_bills")
    save_csv(df, CONGRESS_CSV)
    return df


def merge_and_export(min_score: int = 5) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    if FED_REGISTER_CSV.exists():
        parts.append(pd.read_csv(FED_REGISTER_CSV))
    if CONGRESS_CSV.exists():
        parts.append(pd.read_csv(CONGRESS_CSV))
    if not parts:
        raise FileNotFoundError("No processed CSVs to merge.")

    combined = pd.concat(parts, ignore_index=True)
    save_csv(combined, COMBINED_CSV)

    top = combined.sort_values("opportunity_score", ascending=False, ignore_index=True)
    top[top["opportunity_score"] >= min_score].to_csv(TOP_CSV, index=False)
    log.info("Wrote %d combined rows; top scored saved to %s", len(combined), TOP_CSV)
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the policy data pipeline.")
    parser.add_argument(
        "--skip-fed", action="store_true", help="Skip federal register processing."
    )
    parser.add_argument(
        "--skip-congress", action="store_true", help="Skip congress bills processing."
    )
    parser.add_argument(
        "--min-score", type=int, default=5, help="Minimum score for top_opportunities.csv."
    )
    args = parser.parse_args()

    if not args.skip_fed:
        try:
            run_federal_register()
        except FileNotFoundError as exc:
            log.warning("%s", exc)
    if not args.skip_congress:
        try:
            run_congress()
        except FileNotFoundError as exc:
            log.warning("%s", exc)
    merge_and_export(min_score=args.min_score)


if __name__ == "__main__":
    main()
