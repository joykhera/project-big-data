from dataclasses import dataclass, asdict


MARKET_HINT_WORDS = {
    "healthcare", "finance", "security", "education", "robotics", "automation",
    "energy", "supply", "logistics", "retail", "manufacturing", "compliance",
}


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


def _score_opportunity(keyword: str, point: str, index: int) -> int:
    market = 25 if keyword in MARKET_HINT_WORDS else 16
    clarity = 18 if len(point) >= 100 else 12
    feasibility = max(15, 27 - index * 2)
    novelty = 22 if any(x in point.lower() for x in ("novel", "improve", "outperform")) else 16
    total = min(100, market + clarity + feasibility + novelty)
    return total


def generate_opportunities(
    keywords: list[tuple[str, int]],
    key_points: list[str],
    count: int = 5,
) -> list[Opportunity]:
    if not keywords or not key_points:
        return []

    results: list[Opportunity] = []
    for idx in range(count):
        keyword = keywords[idx % len(keywords)][0]
        point = key_points[idx % len(key_points)]
        score = _score_opportunity(keyword, point, idx)

        results.append(
            Opportunity(
                title=f"{keyword.title()} Operations Assistant",
                target_user=f"Teams working with {keyword}",
                problem_statement=f"Teams struggle to apply the paper insight in day-to-day {keyword} workflows.",
                solution_outline=f"Use this core insight as a product rule engine: {point[:170].rstrip('.')}.",
                revenue_model="Monthly B2B subscription + onboarding support.",
                mvp_scope=f"Week 1: ingestion. Week 2: rule-based recommendations for {keyword}. Week 3: dashboard and export.",
                risk_note="Paper accuracy in real-world environment can vary; pilot with a narrow user group first.",
                score=score,
            )
        )
    return results

