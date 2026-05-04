"""Industry tagging based on keyword presence in policy text."""

from __future__ import annotations

import pandas as pd

INDUSTRY_KEYWORDS: dict[str, list[str]] = {
    "energy": ["energy", "solar", "wind", "electricity", "power", "renewable"],
    "healthcare": ["health", "hospital", "cdc", "medical", "medicare", "medicaid"],
    "transportation": ["transport", "rail", "airport", "highway", "transit"],
    "housing": ["housing", "real estate", "rent", "mortgage", "homeless"],
    "environment": ["climate", "environment", "epa", "emissions", "pollution"],
    "finance": ["bank", "finance", "loan", "investment", "securities"],
    "labor": ["worker", "employment", "labor", "wage", "union"],
}


def tag_industries(text: str) -> list[str]:
    text = str(text or "").lower()
    return [
        industry
        for industry, keywords in INDUSTRY_KEYWORDS.items()
        if any(kw in text for kw in keywords)
    ]


def apply_industry_tags(df: pd.DataFrame) -> pd.DataFrame:
    df["industry_tags"] = df["text"].apply(tag_industries)
    return df
