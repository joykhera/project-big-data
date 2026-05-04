
from project_big_data.paper_tool import storage as storage_mod
from project_big_data.paper_tool.opportunities import Opportunity
from project_big_data.paper_tool.storage import (
    append_history,
    export_csv_bytes,
    load_history,
    opportunities_to_dataframe,
)


def _opp(score: int = 70) -> Opportunity:
    return Opportunity(
        title="Test Title",
        target_user="Test users",
        problem_statement="The problem.",
        solution_outline="The solution.",
        revenue_model="Subscription",
        mvp_scope="M1: build. M2: ship.",
        risk_note="Some risk.",
        score=score,
    )


def test_opportunities_to_dataframe_round_trip():
    df = opportunities_to_dataframe([_opp(80), _opp(60)])
    assert list(df.columns) == [
        "title", "target_user", "problem_statement", "solution_outline",
        "revenue_model", "mvp_scope", "risk_note", "score",
    ]
    assert df["score"].tolist() == [80, 60]


def test_export_csv_bytes_is_bytes():
    df = opportunities_to_dataframe([_opp()])
    out = export_csv_bytes(df)
    assert isinstance(out, bytes)
    assert b"Test Title" in out


def test_append_history_creates_then_appends(tmp_path, monkeypatch):
    history = tmp_path / "history.csv"
    monkeypatch.setattr(storage_mod, "HISTORY_PATH", history)

    append_history("Paper One", "Upload PDF", [_opp(80)])
    df = load_history()
    assert len(df) == 1
    assert df.iloc[0]["paper_title"] == "Paper One"

    append_history("Paper Two", "Search arXiv", [_opp(70), _opp(60)])
    df = load_history()
    assert len(df) == 3
    assert set(df["paper_title"]) == {"Paper One", "Paper Two"}


def test_load_history_empty_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_mod, "HISTORY_PATH", tmp_path / "nope.csv")
    assert load_history().empty
