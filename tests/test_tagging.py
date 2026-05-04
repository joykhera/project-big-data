import pandas as pd

from project_big_data.policy.processing.tagging import (
    apply_industry_tags,
    tag_industries,
)


def test_tag_industries_basic():
    assert "healthcare" in tag_industries("CDC issues guidance on hospital protocols")
    assert "energy" in tag_industries("renewable solar power expansion")
    assert "finance" in tag_industries("bank loan disclosure rule")


def test_tag_industries_multiple_tags():
    tags = tag_industries("Hospital workers in housing complexes")
    assert set(tags) == {"healthcare", "housing", "labor"}


def test_tag_industries_no_match_returns_empty():
    assert tag_industries("unrelated text about general policy") == []


def test_tag_industries_handles_none():
    assert tag_industries(None) == []  # type: ignore[arg-type]
    assert tag_industries("") == []


def test_apply_industry_tags_adds_column():
    df = pd.DataFrame({"text": ["energy rule", "no match here"]})
    out = apply_industry_tags(df)
    assert out["industry_tags"].iloc[0] == ["energy"]
    assert out["industry_tags"].iloc[1] == []
