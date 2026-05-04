import urllib.parse
import xml.etree.ElementTree as ET

import requests


def _clean(value: str) -> str:
    return " ".join((value or "").split())


def search_arxiv_papers(query: str, max_results: int = 8) -> list[dict]:
    safe_query = urllib.parse.quote(query.strip())
    url = (
        "https://export.arxiv.org/api/query?"
        f"search_query=all:{safe_query}&start=0&max_results={max_results}"
    )
    response = requests.get(url, timeout=25, headers={"User-Agent": "paper-opportunity-mvp/1.0"})
    response.raise_for_status()

    root = ET.fromstring(response.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    papers: list[dict] = []
    for entry in root.findall("atom:entry", ns):
        title = _clean(entry.findtext("atom:title", "", ns))
        summary = _clean(entry.findtext("atom:summary", "", ns))
        paper_link = ""
        pdf_link = ""

        for link_node in entry.findall("atom:link", ns):
            href = link_node.attrib.get("href", "")
            title_attr = link_node.attrib.get("title", "")
            if not paper_link and href.startswith("http"):
                paper_link = href
            if title_attr == "pdf":
                pdf_link = href

        papers.append(
            {
                "title": title,
                "summary": summary,
                "paper_link": paper_link,
                "pdf_link": pdf_link,
            }
        )
    return papers


def download_pdf_bytes(url: str) -> bytes:
    response = requests.get(url, timeout=30, headers={"User-Agent": "paper-opportunity-mvp/1.0"})
    response.raise_for_status()
    return response.content

