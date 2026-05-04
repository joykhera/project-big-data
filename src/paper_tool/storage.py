from io import StringIO
from pathlib import Path
from datetime import datetime
from typing import Any

import pandas as pd

from src.paper_tool.opportunity_engine import Opportunity


HISTORY_PATH = Path("data/processed/paper_opportunity_history.csv")


def opportunities_to_dataframe(opportunities: list[Opportunity]) -> pd.DataFrame:
    return pd.DataFrame([item.to_dict() for item in opportunities])


def export_csv_bytes(df: pd.DataFrame) -> bytes:
    buffer = StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def append_history(paper_title: str, source: str, opportunities: list[Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in opportunities:
        row = item.to_dict() if hasattr(item, "to_dict") else dict(item)
        row["paper_title"] = paper_title
        row["source"] = source
        row["run_time"] = run_time
        rows.append(row)

    new_df = pd.DataFrame(rows)
    if HISTORY_PATH.exists():
        old_df = pd.read_csv(HISTORY_PATH)
        combined = pd.concat([old_df, new_df], ignore_index=True)
        combined.to_csv(HISTORY_PATH, index=False)
    else:
        new_df.to_csv(HISTORY_PATH, index=False)


def load_history() -> pd.DataFrame:
    if not HISTORY_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(HISTORY_PATH)

