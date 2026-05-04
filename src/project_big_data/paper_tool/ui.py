"""Streamlit UI for the paper -> opportunity flow."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from project_big_data.config import ANTHROPIC_API_KEY
from project_big_data.paper_tool.analysis import (
    clean_text,
    extract_key_points,
    top_keywords,
)
from project_big_data.paper_tool.arxiv_client import (
    PaperHit,
    download_pdf_bytes,
    search_arxiv_papers,
)
from project_big_data.paper_tool.opportunities import generate_opportunities
from project_big_data.paper_tool.pdf_tools import extract_text_from_pdf
from project_big_data.paper_tool.storage import (
    append_history,
    export_csv_bytes,
    load_history,
    opportunities_to_dataframe,
)


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_arxiv_search(query: str, max_results: int) -> list[dict]:
    return [hit.__dict__ for hit in search_arxiv_papers(query, max_results)]


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_pdf_text(pdf_bytes: bytes) -> str:
    return extract_text_from_pdf(pdf_bytes)


def _paper_source_panel() -> tuple[str, str, str]:
    st.subheader("1) Select paper source")
    mode = st.radio("Source", ["Upload PDF", "Search arXiv"], horizontal=True)

    if mode == "Upload PDF":
        uploaded = st.file_uploader("Research paper (PDF)", type=["pdf"])
        if uploaded is None:
            return mode, "", ""
        with st.spinner("Extracting text..."):
            text = _cached_pdf_text(uploaded.getvalue())
        st.success(f"Loaded `{uploaded.name}` ({len(text.split())} words).")
        return mode, uploaded.name, text

    query = st.text_input("arXiv topic", value="ai healthcare")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Search papers"):
            try:
                st.session_state["arxiv_results"] = _cached_arxiv_search(query, 8)
            except Exception as exc:
                st.error(f"Search failed: {exc}")
    with col2:
        full_pdf = st.checkbox("Try full PDF parse (slower)", value=False)

    results = [PaperHit(**r) for r in st.session_state.get("arxiv_results", [])]
    if not results:
        return mode, "", ""

    options = {f"{i + 1}. {hit.display_title}": hit for i, hit in enumerate(results)}
    selected = options[st.selectbox("Pick one paper", list(options))]
    st.markdown(f"[Open paper page]({selected.paper_link})  ·  *{selected.primary_category}*")

    if full_pdf and selected.pdf_link and st.button("Load selected PDF"):
        try:
            with st.spinner("Downloading + parsing PDF..."):
                pdf_bytes = download_pdf_bytes(selected.pdf_link)
                text = _cached_pdf_text(pdf_bytes)
            st.success("Loaded full paper.")
            return mode, selected.display_title, text
        except Exception as exc:
            st.warning(f"PDF parse failed; falling back to abstract. ({exc})")

    return mode, selected.display_title, clean_text(selected.summary)


def _analysis_panel(paper_text: str) -> tuple[list[tuple[str, float]], list[str]]:
    st.subheader("2) Extract insights")
    keywords = top_keywords(paper_text, top_n=20)
    points = extract_key_points(paper_text, limit=8)

    c1, c2, c3 = st.columns(3)
    c1.metric("Words", len(paper_text.split()))
    c2.metric("Keywords", len(keywords))
    c3.metric("Key points", len(points))

    with st.expander("Text preview"):
        st.write(paper_text[:1500] + ("..." if len(paper_text) > 1500 else ""))

    if keywords:
        df = pd.DataFrame(keywords, columns=["keyword", "relevance"])
        st.bar_chart(df.set_index("keyword")["relevance"].head(12))

    st.markdown("**Key points**")
    for i, p in enumerate(points, 1):
        st.markdown(f"**{i}.** {p}")
    return keywords, points


def _opportunity_panel(
    source_mode: str,
    paper_title: str,
    keywords: list[tuple[str, float]],
    points: list[str],
) -> None:
    st.subheader("3) Generate business opportunities")
    if not ANTHROPIC_API_KEY:
        st.info(
            "No `ANTHROPIC_API_KEY` set — using template fallback. "
            "Set the env var for higher-quality, paper-specific opportunities."
        )

    count = st.slider("How many?", 3, 10, 6)
    min_score = st.slider("Minimum score", 0, 95, 50)

    if st.button("Generate", type="primary"):
        with st.spinner("Generating..."):
            opps = generate_opportunities(keywords, points, count=count, paper_title=paper_title)
        if not opps:
            st.warning("Not enough signal in the paper to generate opportunities.")
            return
        df = opportunities_to_dataframe(opps).sort_values("score", ascending=False)
        st.session_state["generated_opps"] = df

    df = st.session_state.get("generated_opps")
    if df is None or df.empty:
        return
    df = df[df["score"] >= min_score]
    if df.empty:
        st.warning("No opportunities meet the score threshold.")
        return

    st.dataframe(df, use_container_width=True, hide_index=True)
    for idx, row in df.reset_index(drop=True).iterrows():
        with st.expander(f"{idx + 1}. {row['title']} (score: {row['score']})"):
            st.markdown(f"**Target user:** {row['target_user']}")
            st.markdown(f"**Problem:** {row['problem_statement']}")
            st.markdown(f"**Solution:** {row['solution_outline']}")
            st.markdown(f"**Revenue model:** {row['revenue_model']}")
            st.markdown(f"**MVP scope:** {row['mvp_scope']}")
            st.markdown(f"**Risk:** {row['risk_note']}")

    st.download_button(
        "Download opportunities CSV",
        data=export_csv_bytes(df),
        file_name="generated_opportunities.csv",
        mime="text/csv",
    )
    if st.button("Save run to history"):
        append_history(paper_title or "Unknown", source_mode, df.to_dict(orient="records"))
        st.success("Saved.")


def _history_panel() -> None:
    st.subheader("4) Saved runs")
    df = load_history()
    if df.empty:
        st.info("No saved runs yet.")
        return
    st.dataframe(df.sort_values("run_time", ascending=False), use_container_width=True)


def render_paper_tool() -> None:
    st.title("Research Paper -> Business Opportunity")
    st.caption("Search or upload a paper, extract insights, generate scored opportunities, export.")
    source, title, text = _paper_source_panel()
    if text:
        kws, pts = _analysis_panel(text)
        _opportunity_panel(source, title, kws, pts)
    st.divider()
    _history_panel()
    st.caption(f"Run: {datetime.now():%Y-%m-%d %H:%M}")
