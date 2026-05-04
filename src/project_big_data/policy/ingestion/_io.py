"""Shared JSON/CSV helpers for ingestion. Replaces the old try/except-CustomException
wrappers; native exceptions propagate naturally."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from project_big_data.config import RAW_DIR


def save_raw_json(data: Any, prefix: str, folder: Path | None = None) -> Path:
    folder = folder or RAW_DIR
    folder.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # no colons - filesystem-safe
    path = folder / f"{prefix}_{timestamp}.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_csv(df: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
