import re
from collections import Counter


STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "for", "on", "with", "at", "by",
    "from", "as", "is", "was", "are", "be", "has", "have", "had", "it", "its", "this",
    "that", "these", "those", "will", "can", "may", "not", "but", "if", "into", "than",
    "more", "most", "about", "after", "over", "new", "how", "what", "why", "when", "who",
    "all", "any", "out", "up", "so", "we", "you", "your", "our", "their", "they", "them",
    "just", "like", "get", "one", "two", "also", "now", "here", "there", "some", "such",
    "using", "based", "paper", "study", "research", "results", "method", "methods",
    "approach", "model", "models", "data",
}

KEY_POINT_HINTS = (
    "we propose", "we present", "our method", "results show", "significant",
    "improve", "achieve", "outperform", "framework", "application", "limitation",
)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


def extract_words(text: str) -> list[str]:
    text = clean_text(text).lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s-]", " ", text)

    words: list[str] = []
    for word in text.split():
        word = word.strip("-")
        if len(word) < 3 or word in STOPWORDS:
            continue
        words.append(word)
    return words


def top_keywords(text: str, top_n: int = 20) -> list[tuple[str, int]]:
    return Counter(extract_words(text)).most_common(top_n)


def extract_key_points(text: str, limit: int = 6) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", clean_text(text))
    scored: list[tuple[int, str]] = []

    for sentence in sentences:
        s = sentence.strip()
        if len(s) < 60:
            continue
        score = 0
        lower = s.lower()
        for hint in KEY_POINT_HINTS:
            if hint in lower:
                score += 2
        score += min(len(s) // 120, 2)
        scored.append((score, s))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [s for _, s in scored[:limit]]

