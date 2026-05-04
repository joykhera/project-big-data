"""Opportunity generation. Primary path uses Google Gemini with JSON-mode output
for varied, paper-specific ideas. Fallback path produces template-based
opportunities so the app still works without an API key."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass

from project_big_data.config import GEMINI_MODEL, GOOGLE_AI_API_KEY

log = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an experienced startup-studio analyst.
Given a research paper's keywords and key points, generate distinct, *concrete*
business opportunities. Each opportunity should target a specific user, solve a
specific problem the paper enables, and be feasible as an MVP within 3 months.

Avoid generic phrasing like "operations assistant". Vary titles and revenue
models across the list."""

_USER_TEMPLATE = """Paper title: {title}

Top keywords (with relevance scores):
{keywords}

Key points from the paper:
{key_points}

Return EXACTLY {count} opportunities as a JSON array. Each object MUST have:
- "title": short product name (4-8 words, distinct across the list)
- "target_user": specific role and context
- "problem_statement": the pain this paper's insight unlocks
- "solution_outline": how the product applies the insight
- "revenue_model": vary across opportunities (subscription, usage, marketplace, licensing, services)
- "mvp_scope": realistic 3-month build plan
- "risk_note": main execution or market risk
- "score": integer 0-100 reflecting market potential AND technical feasibility

Return ONLY the JSON array, no prose."""


@dataclass
class Opportunity:
    title: str
    target_user: str
    problem_statement: str
    solution_outline: str
    revenue_model: str
    mvp_scope: str
    risk_note: str
    score: int

    def to_dict(self) -> dict:
        return asdict(self)


def _format_keywords(keywords: list[tuple[str, float]]) -> str:
    return "\n".join(f"- {kw} (relevance {score:.2f})" for kw, score in keywords[:15])


def _format_points(points: list[str]) -> str:
    return "\n".join(f"- {p[:300]}" for p in points[:8])


def _parse_response(payload: str) -> list[Opportunity]:
    payload = payload.strip()
    if payload.startswith("```"):
        payload = payload.strip("`")
        payload = payload.split("\n", 1)[1] if "\n" in payload else payload
    if payload.endswith("```"):
        payload = payload.rsplit("```", 1)[0]
    data = json.loads(payload)
    out: list[Opportunity] = []
    for item in data:
        out.append(
            Opportunity(
                title=str(item.get("title", "Untitled")).strip(),
                target_user=str(item.get("target_user", "")).strip(),
                problem_statement=str(item.get("problem_statement", "")).strip(),
                solution_outline=str(item.get("solution_outline", "")).strip(),
                revenue_model=str(item.get("revenue_model", "")).strip(),
                mvp_scope=str(item.get("mvp_scope", "")).strip(),
                risk_note=str(item.get("risk_note", "")).strip(),
                score=int(item.get("score", 0)),
            )
        )
    return out


def _generate_with_gemini(
    title: str,
    keywords: list[tuple[str, float]],
    key_points: list[str],
    count: int,
) -> list[Opportunity]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GOOGLE_AI_API_KEY)
    user_msg = _USER_TEMPLATE.format(
        title=title or "Untitled paper",
        keywords=_format_keywords(keywords),
        key_points=_format_points(key_points),
        count=count,
    )
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_msg,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            response_mime_type="application/json",
            max_output_tokens=4000,
        ),
    )
    return _parse_response(response.text or "")


_FALLBACK_TEMPLATES = [
    ("{kw} Copilot", "subscription"),
    ("{kw} Insights Platform", "usage-based"),
    ("{kw} Marketplace", "marketplace fee"),
    ("{kw} Compliance Suite", "annual licensing"),
    ("{kw} Operations Studio", "services + retainer"),
    ("{kw} Decision Engine", "tiered subscription"),
    ("{kw} Research Workbench", "freemium"),
    ("{kw} Data Cooperative", "membership"),
]


def _fallback(
    keywords: list[tuple[str, float]],
    key_points: list[str],
    count: int,
) -> list[Opportunity]:
    if not keywords or not key_points:
        return []
    out: list[Opportunity] = []
    for i in range(count):
        kw = keywords[i % len(keywords)][0].title()
        point = key_points[i % len(key_points)]
        title_tmpl, model = _FALLBACK_TEMPLATES[i % len(_FALLBACK_TEMPLATES)]
        score = max(50, 90 - i * 5 + (10 if any(s in kw.lower() for s in ("health", "energy", "finance")) else 0))
        out.append(
            Opportunity(
                title=title_tmpl.format(kw=kw),
                target_user=f"Teams already working with {kw.lower()}",
                problem_statement=f"Operationalising the paper insight for {kw.lower()} workflows is manual and slow.",
                solution_outline=f"Productise the insight: {point[:200].rstrip('.')}.",
                revenue_model=model,
                mvp_scope=f"M1 ingest -> M2 rule engine on {kw.lower()} -> M3 dashboard + export.",
                risk_note="Lab-to-field generalisation; pilot narrowly first.",
                score=min(100, score),
            )
        )
    return out


def generate_opportunities(
    keywords: list[tuple[str, float]],
    key_points: list[str],
    count: int = 6,
    paper_title: str = "",
) -> list[Opportunity]:
    if not keywords or not key_points:
        return []
    if GOOGLE_AI_API_KEY:
        try:
            return _generate_with_gemini(paper_title, keywords, key_points, count)
        except Exception as exc:  # pragma: no cover - network-dependent
            log.warning("Gemini generation failed (%s); falling back to templates.", exc)
    return _fallback(keywords, key_points, count)
