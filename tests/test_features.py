import pandas as pd

from project_big_data.policy.processing.features import apply_all_features


def test_apply_all_features_adds_expected_columns():
    df = pd.DataFrame(
        {
            "title": ["Rule on Energy", None],
            "abstract": ["A long abstract.", None],
            "type": ["Rule", "Notice"],
            "agency_names": ["EPA, DOE", None],
        }
    )
    out = apply_all_features(df, source_name="federal_register")
    expected = {
        "source", "text", "has_abstract", "title_length",
        "abstract_length", "agency_count", "policy_stage",
    }
    assert expected <= set(out.columns)
    assert (out["source"] == "federal_register").all()
    assert out["agency_count"].iloc[0] == 2
    assert out["agency_count"].iloc[1] == 0
    assert out["has_abstract"].tolist() == [True, False]
    assert out["policy_stage"].iloc[1] == "Notice"
