"""Composite opportunity scoring across policy stage, industry, text richness, geography."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

POLICY_STAGE_WEIGHTS: dict[str, int] = {
    "Rule": 3,
    "Proposed Rule": 2,
    "Notice": 1,
    "Presidential Document": 3,
}

INDUSTRY_WEIGHTS: dict[str, int] = {
    "energy": 2,
    "healthcare": 1,
    "transportation": 2,
    "housing": 3,
    "environment": 2,
    "finance": 2,
    "labor": 1,
}


def score_policy_stage(stage: str) -> int:
    return POLICY_STAGE_WEIGHTS.get(stage, 0)


def score_industries(tags: Iterable[str]) -> int:
    return sum(INDUSTRY_WEIGHTS.get(t, 0) for t in (tags or []))


def score_text_richness(abstract_length: int) -> int:
    if abstract_length >= 500:
        return 2
    if abstract_length >= 150:
        return 1
    return 0


def score_geography(states: Iterable[str]) -> int:
    return 1 if states else 0


def apply_opportunity_score(df: pd.DataFrame) -> pd.DataFrame:
    df["policy_stage_score"] = df["policy_stage"].apply(score_policy_stage)
    df["industry_score"] = df["industry_tags"].apply(score_industries)
    df["text_score"] = df["abstract_length"].apply(score_text_richness)
    df["geography_score"] = df["states"].apply(score_geography)
    df["opportunity_score"] = (
        df["policy_stage_score"]
        + df["industry_score"]
        + df["text_score"]
        + df["geography_score"]
    )
    return df
