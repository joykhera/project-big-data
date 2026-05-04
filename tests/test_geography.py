import pandas as pd

from project_big_data.policy.processing.geography import (
    apply_geography,
    extract_state,
)


def test_extract_state_finds_full_names_case_insensitive():
    assert "CA" in extract_state("This rule applies in California today.")
    assert "NY" in extract_state("Subject: new york compliance update")


def test_extract_state_finds_abbreviations_word_boundary():
    states = extract_state("Operations in TX and CA expand next quarter.")
    assert "TX" in states
    assert "CA" in states


def test_extract_state_does_not_match_inside_words():
    """The original code matched substrings; this regression test ensures
    word-boundary matching so 'OR' inside 'WORK' doesn't trigger Oregon."""
    assert extract_state("WORK ORDER") != ["OR"]


def test_extract_state_deduplicates():
    result = extract_state("Texas and TX again, Texas yet again.")
    assert result.count("TX") == 1


def test_extract_state_empty_inputs():
    assert extract_state("") == []
    assert extract_state(None) == []  # type: ignore[arg-type]


def test_apply_geography_adds_states_column():
    df = pd.DataFrame({"text": ["California rules", "no states here", "TX & FL"]})
    out = apply_geography(df)
    assert "states" in out.columns
    assert out["states"].iloc[0] == ["CA"]
    assert out["states"].iloc[1] == []
    assert sorted(out["states"].iloc[2]) == ["FL", "TX"]
