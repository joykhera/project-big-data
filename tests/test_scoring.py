import pandas as pd

from project_big_data.policy.processing.scoring import (
    apply_opportunity_score,
    score_geography,
    score_industries,
    score_policy_stage,
    score_text_richness,
)


def test_score_policy_stage():
    assert score_policy_stage("Rule") == 3
    assert score_policy_stage("Proposed Rule") == 2
    assert score_policy_stage("Notice") == 1
    assert score_policy_stage("Unknown") == 0


def test_score_industries_sum():
    assert score_industries(["energy", "housing"]) == 5  # 2 + 3
    assert score_industries([]) == 0
    assert score_industries(["nonexistent"]) == 0


def test_score_text_richness_thresholds():
    assert score_text_richness(0) == 0
    assert score_text_richness(149) == 0
    assert score_text_richness(150) == 1
    assert score_text_richness(499) == 1
    assert score_text_richness(500) == 2


def test_score_geography_truthy():
    assert score_geography(["CA"]) == 1
    assert score_geography([]) == 0


def test_apply_opportunity_score_full_pipeline():
    df = pd.DataFrame(
        {
            "policy_stage": ["Rule", "Notice"],
            "industry_tags": [["healthcare"], ["energy", "labor"]],
            "abstract_length": [600, 100],
            "states": [["CA"], []],
        }
    )
    out = apply_opportunity_score(df)
    assert {"policy_stage_score", "industry_score", "text_score", "geography_score"} <= set(out.columns)
    # Row 0: 3 (Rule) + 1 (healthcare) + 2 (long abstract) + 1 (state) = 7
    assert out["opportunity_score"].iloc[0] == 7
    # Row 1: 1 (Notice) + 3 (energy=2 + labor=1) + 0 (short) + 0 (no state) = 4
    assert out["opportunity_score"].iloc[1] == 4
