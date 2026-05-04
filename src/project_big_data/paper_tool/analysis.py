"""Keyword extraction (YAKE) and extractive summarization (sumy LexRank).
Both are unsupervised, single-document, and run without network or model downloads
beyond NLTK's `punkt` tokenizer (downloaded lazily on first use)."""

from __future__ import annotations

import contextlib
import re
import threading

import yake
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer

_nltk_lock = threading.Lock()
_nltk_ready = False


def _ensure_nltk() -> None:
    """sumy's Tokenizer needs NLTK 'punkt' (and 'punkt_tab' on newer NLTK)."""
    global _nltk_ready
    if _nltk_ready:
        return
    with _nltk_lock:
        if _nltk_ready:
            return
        import nltk

        for resource in ("punkt", "punkt_tab"):
            try:
                nltk.data.find(f"tokenizers/{resource}")
            except LookupError:
                with contextlib.suppress(Exception):
                    nltk.download(resource, quiet=True)
        _nltk_ready = True


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


def top_keywords(text: str, top_n: int = 20) -> list[tuple[str, float]]:
    """Return (keyword, score) tuples. Lower YAKE score == more relevant.
    We invert the score so higher numbers mean more relevant for display."""
    text = clean_text(text)
    if not text:
        return []
    extractor = yake.KeywordExtractor(lan="en", n=2, top=top_n, dedupLim=0.7)
    raw = extractor.extract_keywords(text)
    return [(kw, round(1.0 / (score + 1e-6), 4)) for kw, score in raw]


def extract_key_points(text: str, limit: int = 8) -> list[str]:
    text = clean_text(text)
    if len(text) < 200:
        return [text] if text else []
    _ensure_nltk()
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    return [str(s) for s in summarizer(parser.document, limit)]
