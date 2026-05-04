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


def pill_html(label: str, value: str, *, bg: str = "#f1f5f9", fg: str = "#0f172a") -> str:
    return (
        f'<span style="display:inline-block;padding:3px 10px;margin:2px 4px 2px 0;'
        f'border-radius:999px;background:{bg};color:{fg};font-size:12px;'
        f'font-weight:500;">{label}: {value}</span>'
    )


def opportunity_card(row: dict[str, Any]) -> None:
    score = int(row["score"])
    with st.container(border=True):
        h_left, h_right = st.columns([5, 1])
        with h_left:
            st.markdown(
                f"<div style='font-size:18px;font-weight:600;line-height:1.3;'>"
                f"{row['title']}</div>"
                f"<div style='color:#64748b;font-size:13px;margin-top:4px;'>"
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
                f"<div style='font-size:11px;font-weight:700;color:#dc2626;"
                f"letter-spacing:0.06em;'>PROBLEM</div>"
                f"<div style='font-size:13px;color:#334155;'>{row['problem_statement']}</div>",
                unsafe_allow_html=True,
            )
        with b2:
            st.markdown(
                f"<div style='font-size:11px;font-weight:700;color:#16a34a;"
                f"letter-spacing:0.06em;'>SOLUTION</div>"
                f"<div style='font-size:13px;color:#334155;'>{row['solution_outline']}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")
        st.markdown(
            pill_html("💰 Revenue", str(row["revenue_model"]), bg="#ecfdf5", fg="#065f46")
            + pill_html("⚠ Risk", str(row["risk_note"])[:90], bg="#fef3c7", fg="#92400e"),
            unsafe_allow_html=True,
        )

        with st.expander("MVP scope (3 months)"):
            st.write(row["mvp_scope"])
