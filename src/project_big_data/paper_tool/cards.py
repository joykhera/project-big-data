"""Shared Streamlit card rendering for opportunity grids.
Used by both the manual paper-tool flow and the auto-discovery flow."""

from __future__ import annotations

from typing import Any

import streamlit as st


def score_color(score: int) -> str:
    if score >= 80:
        return "#16a34a"
    if score >= 60:
        return "#d97706"
    return "#dc2626"


def score_badge_html(score: int) -> str:
    color = score_color(score)
    return (
        f'<div style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:48px;height:48px;border-radius:50%;background:{color};color:white;'
        f'font-weight:700;font-size:18px;flex-shrink:0;">{score}</div>'
    )


def pill_html(label: str, value: str, *, bg: str = "#064e3b", fg: str = "#a7f3d0") -> str:
    """Default colors (dark green bg / light green text) read well in both
    light and dark themes; saturated enough to read on white, dark enough to
    read on near-black. Override per-call for category-specific colors."""
    return (
        f'<span style="display:inline-block;padding:3px 10px;margin:2px 4px 2px 0;'
        f'border-radius:999px;background:{bg};color:{fg};font-size:12px;'
        f'font-weight:500;">{label}: {value}</span>'
    )


def opportunity_card(row: dict[str, Any]) -> None:
    """Body text inherits Streamlit's theme color (no hard-coded fg) so the card
    is readable in both light and dark themes. Coloured accents are kept for
    PROBLEM/SOLUTION labels and pills, where the contrast is intentional."""
    score = int(row["score"])
    with st.container(border=True):
        h_left, h_right = st.columns([5, 1])
        with h_left:
            st.markdown(
                f"<div style='font-size:18px;font-weight:600;line-height:1.3;'>"
                f"{row['title']}</div>"
                f"<div style='font-size:13px;margin-top:4px;opacity:0.75;'>"
                f"👤 {row['target_user']}</div>",
                unsafe_allow_html=True,
            )
        with h_right:
            st.markdown(
                f"<div style='display:flex;justify-content:flex-end;'>"
                f"{score_badge_html(score)}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")
        b1, b2 = st.columns(2)
        with b1:
            st.markdown(
                f"<div style='font-size:11px;font-weight:700;color:#ef4444;"
                f"letter-spacing:0.06em;margin-bottom:2px;'>PROBLEM</div>"
                f"<div style='font-size:13px;line-height:1.5;'>{row['problem_statement']}</div>",
                unsafe_allow_html=True,
            )
        with b2:
            st.markdown(
                f"<div style='font-size:11px;font-weight:700;color:#22c55e;"
                f"letter-spacing:0.06em;margin-bottom:2px;'>SOLUTION</div>"
                f"<div style='font-size:13px;line-height:1.5;'>{row['solution_outline']}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")
        st.markdown(
            pill_html("💰 Revenue", str(row["revenue_model"]))
            + pill_html("⚠ Risk", str(row["risk_note"])[:90], bg="#78350f", fg="#fcd34d"),
            unsafe_allow_html=True,
        )

        with st.expander("MVP scope (3 months)"):
            st.write(row["mvp_scope"])
