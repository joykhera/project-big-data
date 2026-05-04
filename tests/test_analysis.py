from project_big_data.paper_tool.analysis import (
    clean_text,
    extract_key_points,
    top_keywords,
)


def test_clean_text_collapses_whitespace():
    assert clean_text("  hello\n\n  world  ") == "hello world"
    assert clean_text("") == ""
    assert clean_text(None) == ""  # type: ignore[arg-type]


def test_top_keywords_returns_relevance_tuples():
    text = (
        "Quantum computing accelerates molecular simulations. Quantum algorithms "
        "outperform classical methods on specific problems. Researchers report "
        "quantum advantage on optimization tasks."
    )
    keywords = top_keywords(text, top_n=5)
    assert keywords
    assert all(isinstance(kw, str) and isinstance(score, float) for kw, score in keywords)
    assert any("quantum" in kw.lower() for kw, _ in keywords)


def test_top_keywords_handles_empty():
    assert top_keywords("") == []


def test_extract_key_points_short_text_returns_text():
    assert extract_key_points("hello") == ["hello"]
    assert extract_key_points("") == []


def test_extract_key_points_returns_sentences_for_longer_text():
    text = " ".join(
        [
            "We propose a novel framework for federated learning across hospitals.",
            "The framework preserves patient privacy by training models locally.",
            "Experimental results show a 15% improvement over baseline methods.",
            "Our approach scales to thousands of edge nodes with minimal overhead.",
            "The system has been validated in three independent clinical settings.",
            "Future work will examine real-time inference at the bedside.",
        ]
    )
    points = extract_key_points(text, limit=3)
    assert 1 <= len(points) <= 3
    assert all(isinstance(p, str) and len(p) > 0 for p in points)
