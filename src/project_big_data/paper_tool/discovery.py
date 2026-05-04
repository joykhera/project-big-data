"""Discovery mode: pulls trending papers from Hugging Face's Daily Papers feed,
runs a single batched Gemini call to rate commercial viability, then generates
business opportunities for the top-ranked papers.

Cost per discovery run (Gemini 2.5 Flash, thinking off):
- 1 batched viability-scoring call (~5K in, ~1K out) ≈ $0.004
- K full opportunity-generation calls (already-existing pipeline) ≈ $0.04
Total: ~$0.05 for K=5 papers from a 30-paper feed.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date

import requests

from project_big_data.config import GEMINI_MODEL, GOOGLE_AI_API_KEY, PROCESSED_DIR
from project_big_data.paper_tool.opportunities import (
    Opportunity,
    generate_opportunities,
)

log = logging.getLogger(__name__)

HF_DAILY_URL = "https://huggingface.co/api/daily_papers"
DISCOVERY_CACHE = PROCESSED_DIR / "discovery_cache.json"


@dataclass
class TrendingPaper:
    paper_id: str
    title: str
    summary: str
    keywords: list[str]
    upvotes: int
    arxiv_url: str
    viability_score: int = 0
    viability_reason: str = ""
    opportunities: list[Opportunity] = field(default_factory=list)


# ---------- HF feed ----------


def fetch_trending_papers(limit: int = 30) -> list[TrendingPaper]:
    """Pull the most-recent Hugging Face Daily Papers (curated, ~30/day)."""
    resp = requests.get(
        HF_DAILY_URL,
        params={"limit": limit},
        timeout=20,
        headers={"User-Agent": "project-big-data/0.1"},
    )
    resp.raise_for_status()
    data = resp.json()

    papers: list[TrendingPaper] = []
    for entry in data:
        p = entry.get("paper", {}) or {}
        paper_id = str(p.get("id", "")).strip()
        if not paper_id:
            continue
        # HF gives ai_summary / ai_keywords — already LLM-distilled, free for us.
        summary = (p.get("ai_summary") or p.get("summary") or "").strip()
        kws_raw = p.get("ai_keywords") or []
        keywords = [str(k).strip() for k in kws_raw if str(k).strip()]
        papers.append(
            TrendingPaper(
                paper_id=paper_id,
                title=str(p.get("title", "")).strip(),
                summary=summary,
                keywords=keywords,
                upvotes=int(p.get("upvotes") or 0),
                arxiv_url=f"https://arxiv.org/abs/{paper_id}",
            )
        )
    return papers


# ---------- batched viability scoring ----------


_VIABILITY_SYSTEM = """You rate research papers on commercial viability for a
startup studio. Rate each paper 0-10 where:
- 0-3: pure theory, no foreseeable product application
- 4-6: applied research, would need significant work to productize
- 7-10: actionable insight a founder could turn into an MVP within 3 months

Reward: clear use cases, measurable metrics, applied domains.
Penalize: pure benchmarks without real-world hooks, surveys, replication studies."""


def _score_viability_batch(
    papers: list[TrendingPaper],
) -> dict[str, tuple[int, str]]:
    """Returns {paper_id: (score, reason)}. Single batched LLM call."""
    if not GOOGLE_AI_API_KEY or not papers:
        return {}

    from google import genai
    from google.genai import types

    inputs = [
        {
            "id": p.paper_id,
            "title": p.title,
            "summary": p.summary[:600],
            "upvotes": p.upvotes,
        }
        for p in papers
    ]

    user_msg = (
        "Rate each paper below 0-10 for commercial viability. "
        "Return a JSON array of objects with keys: id, score (int 0-10), "
        "reason (string under 25 words). One object per input paper.\n\n"
        + json.dumps(inputs, indent=2)
    )

    client = genai.Client(api_key=GOOGLE_AI_API_KEY)
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_msg,
        config=types.GenerateContentConfig(
            system_instruction=_VIABILITY_SYSTEM,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            max_output_tokens=4096,
        ),
    )
    try:
        parsed = json.loads(resp.text or "[]")
    except json.JSONDecodeError as exc:
        log.warning("Viability batch parse failed: %s", exc)
        return {}
    out: dict[str, tuple[int, str]] = {}
    for item in parsed:
        pid = str(item.get("id", "")).strip()
        if not pid:
            continue
        try:
            out[pid] = (int(item.get("score", 0)), str(item.get("reason", "")))
        except (TypeError, ValueError):
            continue
    return out


# ---------- caching ----------


def _load_cache() -> dict:
    if not DISCOVERY_CACHE.exists():
        return {}
    try:
        return json.loads(DISCOVERY_CACHE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_cache(payload: dict) -> None:
    DISCOVERY_CACHE.parent.mkdir(parents=True, exist_ok=True)
    DISCOVERY_CACHE.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def _serialize_papers(papers: list[TrendingPaper]) -> list[dict]:
    return [
        {
            "paper_id": p.paper_id,
            "title": p.title,
            "summary": p.summary,
            "keywords": p.keywords,
            "upvotes": p.upvotes,
            "arxiv_url": p.arxiv_url,
            "viability_score": p.viability_score,
            "viability_reason": p.viability_reason,
            "opportunities": [o.to_dict() for o in p.opportunities],
        }
        for p in papers
    ]


def _deserialize_papers(payload: list[dict]) -> list[TrendingPaper]:
    out: list[TrendingPaper] = []
    for item in payload:
        opps = [Opportunity(**o) for o in item.get("opportunities", [])]
        out.append(
            TrendingPaper(
                paper_id=item["paper_id"],
                title=item["title"],
                summary=item["summary"],
                keywords=item.get("keywords", []),
                upvotes=item.get("upvotes", 0),
                arxiv_url=item.get("arxiv_url", ""),
                viability_score=item.get("viability_score", 0),
                viability_reason=item.get("viability_reason", ""),
                opportunities=opps,
            )
        )
    return out


# ---------- main entry ----------


def discover_opportunities(
    feed_size: int = 30,
    top_k: int = 5,
    opps_per_paper: int = 4,
    use_cache: bool = True,
) -> list[TrendingPaper]:
    """Pull trending papers, score viability, generate opportunities for top K.

    Cached by today's date so repeat clicks within the day don't re-bill.
    Set use_cache=False to force a fresh run.
    """
    today = date.today().isoformat()
    cache = _load_cache()
    if use_cache and cache.get("date") == today and cache.get("top_k") >= top_k:
        log.info("Loading discovery from cache (%s)", today)
        return _deserialize_papers(cache["papers"])[:top_k]

    log.info("Fetching trending papers (limit=%d)", feed_size)
    papers = fetch_trending_papers(limit=feed_size)
    if not papers:
        return []

    # 1) Sort by upvotes as a coarse signal, take top 2*K candidates
    candidates = sorted(papers, key=lambda p: p.upvotes, reverse=True)[: max(top_k * 3, 10)]

    # 2) Single batched LLM viability score across candidates
    scores = _score_viability_batch(candidates)
    for p in candidates:
        s, r = scores.get(p.paper_id, (0, ""))
        p.viability_score = s
        p.viability_reason = r

    # 3) Re-rank by viability_score, then upvotes
    ranked = sorted(
        candidates, key=lambda p: (p.viability_score, p.upvotes), reverse=True
    )
    selected = ranked[:top_k]

    # 4) Full opportunity generation only for the selected top K
    for p in selected:
        kws = [(k, 1.0) for k in (p.keywords or [])][:10]
        if not kws:
            kws = [(p.title.split()[0] if p.title else "research", 1.0)]
        points = [s.strip() for s in p.summary.split(". ") if s.strip()][:6]
        if not points:
            points = [p.summary[:300]] if p.summary else ["Research insight."]
        try:
            p.opportunities = generate_opportunities(
                kws, points, count=opps_per_paper, paper_title=p.title
            )
        except Exception as exc:  # pragma: no cover - network-dependent
            log.warning("Opportunity gen failed for %s: %s", p.paper_id, exc)
            p.opportunities = []

    _save_cache(
        {
            "date": today,
            "top_k": top_k,
            "papers": _serialize_papers(selected),
        }
    )
    return selected
