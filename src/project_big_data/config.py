"""Project-wide configuration: paths, env vars, and model identifiers."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def project_root() -> Path:
    """Return the directory that contains `pyproject.toml`, `app.py`, and `data/`."""
    return Path(__file__).resolve().parents[2]


DATA_DIR: Path = project_root() / "data"
RAW_DIR: Path = DATA_DIR / "raw_data"
PROCESSED_DIR: Path = DATA_DIR / "processed"
LOGS_DIR: Path = project_root() / "logs"

GOOGLE_AI_API_KEY: str | None = os.getenv("GOOGLE_AI_API_KEY")
CONGRESS_API_KEY: str | None = os.getenv("CONGRESS_API_KEY")

GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
