"""Streamlit UI for the paper -> opportunity flow."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from project_big_data.config import GOOGLE_AI_API_KEY
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
from project_big_data.paper_tool.cards import opportunity_card
from project_big_data.paper_tool.opportunities import generate_opportunities
from project_big_data.paper_tool.pdf_tools import extract_text_from_pdf
from project_big_data.paper_tool.storage import (
    append_history,
    export_csv_bytes,
    load_history,
    opportunities_to_dataframe,
)

# ---------- caching ----------


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_arxiv_search(query: str, max_results: int) -> list[dict]:
    return [hit.__dict__ for hit in search_arxiv_papers(query, max_results)]


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_pdf_text(pdf_bytes: bytes) -> str:
    return extract_text_from_pdf(pdf_bytes)


# ---------- panels ----------


def _paper_source_panel() -> tuple[str, str, str]:
    st.subheader("1. Select a paper")
    mode = st.radio(
        "Source", ["Upload PDF", "Search arXiv"], horizontal=True, label_visibility="collapsed"
    )

    if mode == "Upload PDF":
        uploaded = st.file_uploader("Research paper (PDF)", type=["pdf"])
        if uploaded is None:
            return mode, "", ""
        with st.spinner("Extracting text..."):
            text = _cached_pdf_text(uploaded.getvalue())
        st.success(f"Loaded `{uploaded.name}` — {len(text.split()):,} words")
        return mode, uploaded.name, text

    query = st.text_input("arXiv topic", value="ai healthcare")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Search papers", use_container_width=True):
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
    st.markdown(
        f"[Open paper page]({selected.paper_link})  ·  *{selected.primary_category}*"
    )

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
    st.subheader("2. Extract insights")
    keywords = top_keywords(paper_text, top_n=20)
    points = extract_key_points(paper_text, limit=8)

    c1, c2, c3 = st.columns(3)
    c1.metric("Words", f"{len(paper_text.split()):,}")
    c2.metric("Keywords", len(keywords))
    c3.metric("Key points", len(points))

    tab_kw, tab_pts, tab_text = st.tabs(["Keywords", "Key points", "Text preview"])
    with tab_kw:
        if keywords:
            df = pd.DataFrame(keywords, columns=["keyword", "relevance"])
            st.bar_chart(df.set_index("keyword")["relevance"].head(12))
        else:
            st.info("No keywords detected.")
    with tab_pts:
        if points:
            for p in points:
                st.markdown(f"- {p}")
        else:
            st.info("No key points detected.")
    with tab_text:
        st.write(paper_text[:1500] + ("..." if len(paper_text) > 1500 else ""))
    return keywords, points


def _opportunity_panel(
    source_mode: str,
    paper_title: str,
    keywords: list[tuple[str, float]],
    points: list[str],
) -> None:
    st.subheader("3. Generate business opportunities")
    if not GOOGLE_AI_API_KEY:
        st.info(
            "No `GOOGLE_AI_API_KEY` set — using template fallback. "
            "Set the env var for higher-quality, paper-specific opportunities."
        )

    g_left, g_right = st.columns([3, 1])
    with g_left:
        count = st.slider("How many?", 3, 10, 6)
    with g_right:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        generate = st.button("Generate", type="primary", use_container_width=True)

    if generate:
        with st.spinner("Generating..."):
            opps = generate_opportunities(
                keywords, points, count=count, paper_title=paper_title
            )
        if not opps:
            st.warning("Not enough signal in the paper to generate opportunities.")
            return
        st.session_state["generated_opps"] = opportunities_to_dataframe(opps)
        # auto-persist every successful run so users don't have to click save
        append_history(paper_title or "Unknown", source_mode, opps)
        st.toast(f"Saved {len(opps)} opportunities to history.", icon="💾")

    df = st.session_state.get("generated_opps")
    if df is None or df.empty:
        return

    # ---- post-generation filters in sidebar ----
    st.sidebar.markdown("### Filter opportunities")
    score_lo, score_hi = int(df["score"].min()), int(df["score"].max())
    if score_lo == score_hi:
        score_lo, score_hi = max(0, score_lo - 1), min(100, score_hi + 1)
    score_range = st.sidebar.slider(
        "Score range", 0, 100, (max(0, int(df["score"].min())), 100)
    )
    revenue_models = sorted(df["revenue_model"].dropna().unique().tolist())
    selected_models = st.sidebar.multiselect(
        "Revenue model", revenue_models, default=revenue_models
    )
    sort_by = st.sidebar.radio(
        "Sort by", ["Score (high → low)", "Score (low → high)", "Title"], index=0
    )

    filtered = df[
        df["score"].between(score_range[0], score_range[1])
        & df["revenue_model"].isin(selected_models)
    ].copy()
    if sort_by == "Score (high → low)":
        filtered = filtered.sort_values("score", ascending=False)
    elif sort_by == "Score (low → high)":
        filtered = filtered.sort_values("score", ascending=True)
    else:
        filtered = filtered.sort_values("title")

    if filtered.empty:
        st.warning("No opportunities match the current filters.")
        return

    # ---- summary metrics ----
    m1, m2, m3 = st.columns(3)
    m1.metric("Showing", f"{len(filtered)} / {len(df)}")
    m2.metric("Avg score", f"{filtered['score'].mean():.0f}")
    m3.metric("Top score", int(filtered["score"].max()))

    # ---- card grid (2 cols) ----
    rows = filtered.reset_index(drop=True).to_dict(orient="records")
    for i in range(0, len(rows), 2):
        col_a, col_b = st.columns(2, gap="medium")
        with col_a:
            opportunity_card(rows[i])
        if i + 1 < len(rows):
            with col_b:
                opportunity_card(rows[i + 1])

    # ---- actions ----
    st.markdown("")
    st.download_button(
        "⬇ Download filtered CSV",
        data=export_csv_bytes(filtered),
        file_name="generated_opportunities.csv",
        mime="text/csv",
    )
    st.caption(
        "Every Generate auto-saves the full result set to history (see panel below)."
    )


def _history_panel() -> None:
    df = load_history()
    if df.empty:
        return
    with st.expander(f"Saved runs ({len(df)})"):
        st.dataframe(
            df.sort_values("run_time", ascending=False), use_container_width=True
        )


def render_paper_tool() -> None:
    st.title("Research Paper → Business Opportunity")
    st.caption(
        "Search or upload a paper, extract insights, generate scored business "
        "opportunities, and export."
    )
    source, title, text = _paper_source_panel()
    if text:
        kws, pts = _analysis_panel(text)
        st.divider()
        _opportunity_panel(source, title, kws, pts)
    st.divider()
    _history_panel()
    st.caption(f"Last run: {datetime.now():%Y-%m-%d %H:%M}")
