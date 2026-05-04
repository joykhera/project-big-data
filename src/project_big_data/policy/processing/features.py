"""Feature engineering for unified policy documents."""

from __future__ import annotations

import pandas as pd


def add_source(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    df["source"] = source_name
    return df


def add_text_column(df: pd.DataFrame) -> pd.DataFrame:
    df["text"] = df["title"].fillna("") + " " + df["abstract"].fillna("")
    return df


def add_has_abstract(df: pd.DataFrame) -> pd.DataFrame:
    df["has_abstract"] = df["abstract"].notna()
    return df


def add_title_length(df: pd.DataFrame) -> pd.DataFrame:
    df["title_length"] = df["title"].fillna("").str.len()
    return df


def add_abstract_length(df: pd.DataFrame) -> pd.DataFrame:
    df["abstract_length"] = df["abstract"].fillna("").str.len()
    return df


def add_agency_count(df: pd.DataFrame) -> pd.DataFrame:
    df["agency_count"] = (
        df["agency_names"].fillna("").apply(
            lambda x: len([n for n in str(x).split(",") if n.strip()])
        )
    )
    return df


def add_policy_stage(df: pd.DataFrame) -> pd.DataFrame:
    df["policy_stage"] = df["type"].fillna("unknown")
    return df


def apply_all_features(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    df = add_source(df, source_name)
    df = add_text_column(df)
    df = add_has_abstract(df)
    df = add_title_length(df)
    df = add_abstract_length(df)
    df = add_agency_count(df)
    df = add_policy_stage(df)
    return df
