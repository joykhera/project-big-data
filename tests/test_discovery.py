

from project_big_data.paper_tool import discovery as disc
from project_big_data.paper_tool.discovery import TrendingPaper
from project_big_data.paper_tool.opportunities import Opportunity


def _opp(score=70):
    return Opportunity(
        title="t", target_user="u", problem_statement="p",
        solution_outline="s", revenue_model="r", mvp_scope="m",
        risk_note="rn", score=score,
    )


def _paper(pid: str, score: int = 0, opps=None) -> TrendingPaper:
    return TrendingPaper(
        paper_id=pid,
        title=f"Paper {pid}",
        summary="A summary.",
        keywords=["alpha", "beta"],
        upvotes=10,
        arxiv_url=f"https://arxiv.org/abs/{pid}",
        viability_score=score,
        opportunities=opps or [],
    )


def test_serialize_round_trip():
    papers = [_paper("2400.0001", 8, [_opp(80), _opp(60)]), _paper("2400.0002", 5)]
    serialized = disc._serialize_papers(papers)
    restored = disc._deserialize_papers(serialized)
    assert len(restored) == 2
    assert restored[0].paper_id == "2400.0001"
    assert restored[0].viability_score == 8
    assert len(restored[0].opportunities) == 2
    assert restored[0].opportunities[0].score == 80


def test_cache_load_returns_empty_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(disc, "DISCOVERY_CACHE", tmp_path / "missing.json")
    assert disc._load_cache() == {}


def test_cache_save_and_load(tmp_path, monkeypatch):
    cache_file = tmp_path / "cache.json"
    monkeypatch.setattr(disc, "DISCOVERY_CACHE", cache_file)
    payload = {"date": "2026-05-04", "top_k": 3, "papers": []}
    disc._save_cache(payload)
    assert cache_file.exists()
    assert disc._load_cache() == payload


def test_cache_load_handles_corrupt(tmp_path, monkeypatch):
    cache_file = tmp_path / "cache.json"
    cache_file.write_text("not valid json")
    monkeypatch.setattr(disc, "DISCOVERY_CACHE", cache_file)
    assert disc._load_cache() == {}


def test_score_viability_batch_returns_empty_without_key(monkeypatch):
    monkeypatch.setattr(disc, "GOOGLE_AI_API_KEY", None)
    result = disc._score_viability_batch([_paper("x")])
    assert result == {}


def test_discover_uses_cache_when_fresh(tmp_path, monkeypatch):
    cache_file = tmp_path / "cache.json"
    monkeypatch.setattr(disc, "DISCOVERY_CACHE", cache_file)
    from datetime import date
    today = date.today().isoformat()
    cached = [_paper("2400.0001", 9, [_opp(85)])]
    disc._save_cache(
        {"date": today, "top_k": 3, "papers": disc._serialize_papers(cached)}
    )

    def boom(*_a, **_kw):
        raise AssertionError("network call should not happen with valid cache")

    monkeypatch.setattr(disc, "fetch_trending_papers", boom)
    monkeypatch.setattr(disc, "_score_viability_batch", boom)

    result = disc.discover_opportunities(top_k=3)
    assert len(result) == 1
    assert result[0].paper_id == "2400.0001"
    assert result[0].viability_score == 9


def test_discover_force_refresh_bypasses_cache(tmp_path, monkeypatch):
    cache_file = tmp_path / "cache.json"
    monkeypatch.setattr(disc, "DISCOVERY_CACHE", cache_file)

    monkeypatch.setattr(disc, "fetch_trending_papers", lambda limit: [])
    result = disc.discover_opportunities(top_k=3, use_cache=False)
    assert result == []


def test_fetch_trending_papers_parses_hf_shape(monkeypatch):
    sample = [
        {
            "paper": {
                "id": "2400.0001",
                "title": "Test Paper",
                "summary": "A useful summary.",
                "ai_summary": "An even better AI summary.",
                "ai_keywords": ["alpha", "beta"],
                "upvotes": 42,
            }
        },
        {"paper": {"id": "", "title": "blank id"}},  # filtered out
    ]

    class FakeResp:
        status_code = 200

        def raise_for_status(self): ...

        def json(self):
            return sample

    monkeypatch.setattr(disc.requests, "get", lambda *_a, **_kw: FakeResp())
    papers = disc.fetch_trending_papers(limit=10)
    assert len(papers) == 1
    p = papers[0]
    assert p.paper_id == "2400.0001"
    assert p.upvotes == 42
    assert p.summary == "An even better AI summary."  # ai_summary preferred
    assert p.keywords == ["alpha", "beta"]
    assert p.arxiv_url == "https://arxiv.org/abs/2400.0001"
