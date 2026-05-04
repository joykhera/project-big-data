"""Streamlit UI for the auto-discovery flow."""

from __future__ import annotations

import streamlit as st

from project_big_data.config import GOOGLE_AI_API_KEY
from project_big_data.paper_tool.cards import opportunity_card
from project_big_data.paper_tool.discovery import (
    TrendingPaper,
    discover_opportunities,
)
from project_big_data.paper_tool.opportunities import Opportunity


def _viability_pill(score: int) -> str:
    if score >= 7:
        bg, fg, label = "#dcfce7", "#166534", "🟢 High"
    elif score >= 4:
        bg, fg, label = "#fef3c7", "#92400e", "🟡 Medium"
    else:
        bg, fg, label = "#fee2e2", "#991b1b", "🔴 Low"
    return (
        f"<span style='display:inline-block;padding:3px 10px;border-radius:999px;"
        f"background:{bg};color:{fg};font-size:12px;font-weight:600;'>"
        f"{label} viability ({score}/10)</span>"
    )


def _render_paper_block(paper: TrendingPaper) -> None:
    with st.container(border=True):
        h_left, h_right = st.columns([4, 1])
        with h_left:
            st.markdown(
                f"<div style='font-size:18px;font-weight:600;line-height:1.3;'>"
                f"{paper.title}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='color:#64748b;font-size:13px;margin-top:4px;'>"
                f"<a href='{paper.arxiv_url}' target='_blank'>{paper.paper_id}</a>"
                f"  ·  ⬆ {paper.upvotes} upvotes</div>",
                unsafe_allow_html=True,
            )
        with h_right:
            st.markdown(
                f"<div style='display:flex;justify-content:flex-end;'>"
                f"{_viability_pill(paper.viability_score)}</div>",
                unsafe_allow_html=True,
            )
        if paper.viability_reason:
            st.caption(f"Why: {paper.viability_reason}")

        if not paper.opportunities:
            st.info("No opportunities generated for this paper.")
            return

        # opportunities as 2-col card grid
        rows = [
            o.to_dict() if isinstance(o, Opportunity) else o for o in paper.opportunities
        ]
        for i in range(0, len(rows), 2):
            ca, cb = st.columns(2, gap="medium")
            with ca:
                opportunity_card(rows[i])
            if i + 1 < len(rows):
                with cb:
                    opportunity_card(rows[i + 1])


def render_discovery() -> None:
    st.title("🌟 Discover")
    st.caption(
        "Pull today's trending papers from Hugging Face Daily Papers, rate "
        "their commercial viability, and auto-generate business opportunities "
        "for the top-ranked ones. Cached by date — repeat clicks reuse "
        "today's run."
    )

    if not GOOGLE_AI_API_KEY:
        st.error(
            "Discover mode requires `GOOGLE_AI_API_KEY` to score papers. "
            "Set it in `.env` and reload."
        )
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        feed_size = st.slider("Papers to consider", 10, 50, 30)
    with c2:
        top_k = st.slider("Top-K to deep-dive", 3, 10, 5)
    with c3:
        opps_per_paper = st.slider("Opps per paper", 2, 6, 4)

    col_run, col_force = st.columns([3, 1])
    with col_run:
        run = st.button("Find today's best opportunities", type="primary", use_container_width=True)
    with col_force:
        force = st.checkbox("Force refresh", value=False)

    if run:
        with st.spinner("Fetching feed → scoring viability → generating opportunities..."):
            try:
                papers = discover_opportunities(
                    feed_size=feed_size,
                    top_k=top_k,
                    opps_per_paper=opps_per_paper,
                    use_cache=not force,
                )
            except Exception as exc:
                st.error(f"Discovery failed: {exc}")
                return
        st.session_state["discovery_results"] = papers

    papers = st.session_state.get("discovery_results", [])
    if not papers:
        st.info("Click the button above to discover today's opportunities.")
        return

    total_opps = sum(len(p.opportunities) for p in papers)
    avg_via = sum(p.viability_score for p in papers) / len(papers)
    m1, m2, m3 = st.columns(3)
    m1.metric("Top papers", len(papers))
    m2.metric("Total opportunities", total_opps)
    m3.metric("Avg viability", f"{avg_via:.1f}/10")

    st.divider()
    for paper in papers:
        _render_paper_block(paper)
