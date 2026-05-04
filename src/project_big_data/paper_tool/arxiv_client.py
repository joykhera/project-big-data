"""arXiv search backed by the official `arxiv` Python wrapper, which handles
rate limiting, retries, and pagination per arXiv's terms of use."""

from __future__ import annotations

from dataclasses import dataclass

import arxiv

_client = arxiv.Client(page_size=20, delay_seconds=3.0, num_retries=3)


@dataclass(frozen=True)
class PaperHit:
    title: str
    summary: str
    paper_link: str
    pdf_link: str
    primary_category: str
    published: str

    @property
    def display_title(self) -> str:
        return self.title.replace("\n", " ").strip()


def search_arxiv_papers(query: str, max_results: int = 8) -> list[PaperHit]:
    if not query.strip():
        return []
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    hits: list[PaperHit] = []
    for result in _client.results(search):
        hits.append(
            PaperHit(
                title=result.title,
                summary=result.summary,
                paper_link=result.entry_id,
                pdf_link=result.pdf_url,
                primary_category=result.primary_category,
                published=result.published.isoformat() if result.published else "",
            )
        )
    return hits


def download_pdf_bytes(url: str) -> bytes:
    import requests

    resp = requests.get(url, timeout=30, headers={"User-Agent": "project-big-data/0.1"})
    resp.raise_for_status()
    return resp.content
