"""Detect U.S. states mentioned in policy text."""

from __future__ import annotations

import re

import pandas as pd

_STATES_FULL = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming",
]
_ABBREVIATIONS = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY",
]

# Whole-word matchers; full-name search is case-insensitive, abbreviations are
# case-sensitive to avoid matching "in", "or", etc.
_FULL_RE = re.compile(r"\b(" + "|".join(_STATES_FULL) + r")\b", re.IGNORECASE)
_ABBR_RE = re.compile(r"\b(" + "|".join(_ABBREVIATIONS) + r")\b")
_FULL_TO_ABBR = dict(zip(_STATES_FULL, _ABBREVIATIONS, strict=True))


def extract_state(text: str) -> list[str]:
    """Return de-duplicated list of state abbreviations found in `text`.
    Original code had a bug: `states_found.append()` was called with no argument
    so the list was always empty; downstream geography_score was always 0."""
    if not text:
        return []
    text = str(text)
    found: set[str] = set()
    for match in _FULL_RE.findall(text):
        found.add(_FULL_TO_ABBR[match.title()])
    for match in _ABBR_RE.findall(text):
        found.add(match)
    return sorted(found)


def apply_geography(df: pd.DataFrame) -> pd.DataFrame:
    df["states"] = df["text"].apply(extract_state)
    return df
