from project_big_data.paper_tool.opportunities import (
    Opportunity,
    _fallback,
    _parse_response,
    generate_opportunities,
)


def _kws():
    return [("federated learning", 1.0), ("healthcare", 0.8), ("privacy", 0.6)]


def _points():
    return [
        "We propose federated learning for hospitals.",
        "Patient privacy is preserved by local training.",
        "Results improve over baseline by 15%.",
    ]


def test_fallback_produces_n_distinct_titles():
    opps = _fallback(_kws(), _points(), count=5)
    assert len(opps) == 5
    titles = {o.title for o in opps}
    assert len(titles) == 5  # templates rotate, titles must differ


def test_fallback_varies_revenue_models():
    opps = _fallback(_kws(), _points(), count=8)
    models = {o.revenue_model for o in opps}
    assert len(models) >= 5  # at least 5 different revenue models


def test_fallback_returns_empty_when_no_signal():
    assert _fallback([], _points(), count=3) == []
    assert _fallback(_kws(), [], count=3) == []


def test_parse_response_extracts_opportunities():
    raw = """[
        {
            "title": "Federated Hospital Insights",
            "target_user": "CMIOs at multi-site hospital systems",
            "problem_statement": "Cross-site model training is blocked by HIPAA.",
            "solution_outline": "Deploy a federated trainer with audit logs.",
            "revenue_model": "Annual licensing per facility",
            "mvp_scope": "M1 ingest -> M2 federated trainer -> M3 audit dashboard",
            "risk_note": "Regulatory acceptance varies by state",
            "score": 78
        }
    ]"""
    opps = _parse_response(raw)
    assert len(opps) == 1
    assert opps[0].score == 78
    assert opps[0].revenue_model == "Annual licensing per facility"


def test_parse_response_handles_code_fences():
    raw = "```json\n[]\n```"
    assert _parse_response(raw) == []


def test_generate_opportunities_uses_fallback_when_no_api_key(monkeypatch):
    import project_big_data.paper_tool.opportunities as mod
    monkeypatch.setattr(mod, "GOOGLE_AI_API_KEY", None)
    opps = generate_opportunities(_kws(), _points(), count=3, paper_title="Test")
    assert len(opps) == 3
    assert all(isinstance(o, Opportunity) for o in opps)


def test_generate_opportunities_returns_empty_on_no_signal(monkeypatch):
    import project_big_data.paper_tool.opportunities as mod
    monkeypatch.setattr(mod, "GOOGLE_AI_API_KEY", None)
    assert generate_opportunities([], [], count=5) == []
