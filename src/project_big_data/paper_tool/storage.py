"""History persistence for generated opportunities."""

from __future__ import annotations

from datetime import datetime
from io import StringIO
from typing import Any

import pandas as pd

from project_big_data.config import PROCESSED_DIR
from project_big_data.paper_tool.opportunities import Opportunity

HISTORY_PATH = PROCESSED_DIR / "paper_opportunity_history.csv"


def opportunities_to_dataframe(opps: list[Opportunity]) -> pd.DataFrame:
    return pd.DataFrame([o.to_dict() for o in opps])


def export_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def append_history(paper_title: str, source: str, opportunities: list[Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows: list[dict] = []
    for item in opportunities:
        row = item.to_dict() if hasattr(item, "to_dict") else dict(item)
        row.update({"paper_title": paper_title, "source": source, "run_time": run_time})
        rows.append(row)

    new_df = pd.DataFrame(rows)
    if HISTORY_PATH.exists():
        old_df = pd.read_csv(HISTORY_PATH)
        new_df = pd.concat([old_df, new_df], ignore_index=True)
    new_df.to_csv(HISTORY_PATH, index=False)


def load_history() -> pd.DataFrame:
    if not HISTORY_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(HISTORY_PATH)
