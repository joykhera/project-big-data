"""Streamlit UI for exploring scored policy opportunities."""

from __future__ import annotations

import ast

import pandas as pd
import streamlit as st

from project_big_data.policy.pipeline import TOP_CSV


@st.cache_data(ttl=300, show_spinner=False)
def _load_top() -> pd.DataFrame:
    if not TOP_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(TOP_CSV)


def _parse_tag_list(value: object) -> list[str]:
    """Industry tags / states come back as strings like "['energy', 'finance']"
    after a CSV round-trip. Parse safely."""
    if isinstance(value, list):
        return value
    if not value or pd.isna(value):
        return []
    try:
        parsed = ast.literal_eval(str(value))
        return list(parsed) if isinstance(parsed, (list, tuple)) else []
    except (ValueError, SyntaxError):
        return [s.strip() for s in str(value).split(",") if s.strip()]


def render_policy_dashboard() -> None:
    st.title("Policy Opportunity Dashboard")
    st.caption("Federal Register documents + Congress bills, scored as business opportunities.")

    df = _load_top()
    if df.empty:
        st.error(
            f"No data at `{TOP_CSV}`. Run the pipeline first:\n\n"
            "```bash\npython -m project_big_data.policy.pipeline\n```"
        )
        return

    df["industry_tags_list"] = df["industry_tags"].apply(_parse_tag_list)
    df["states_list"] = df["states"].apply(_parse_tag_list)

    # ----- sidebar filters -----
    st.sidebar.header("Filters")
    sources = sorted(df["source"].dropna().unique())
    selected_sources = st.sidebar.multiselect("Source", sources, default=sources)

    stages = sorted(df["policy_stage"].dropna().unique())
    selected_stages = st.sidebar.multiselect("Policy stage", stages, default=stages)

    score_lo, score_hi = int(df["opportunity_score"].min()), int(df["opportunity_score"].max())
    min_score = st.sidebar.slider("Minimum score", score_lo, score_hi, score_lo)

    all_industries = sorted({tag for tags in df["industry_tags_list"] for tag in tags})
    selected_industries = st.sidebar.multiselect("Industry tags", all_industries, default=[])

    search = st.sidebar.text_input("Title search")

    # ----- filtering (the original code's industry filter was broken: it called
    # isin() on comma-separated strings, which only matches exact strings) -----
    mask = (
        df["source"].isin(selected_sources)
        & df["policy_stage"].isin(selected_stages)
        & (df["opportunity_score"] >= min_score)
    )
    if search.strip():
        mask &= df["title"].fillna("").str.contains(search, case=False, na=False)
    if selected_industries:
        wanted = set(selected_industries)
        mask &= df["industry_tags_list"].apply(lambda tags: bool(wanted & set(tags)))

    filtered = df[mask].copy()

    # ----- summary -----
    st.subheader("Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Opportunities", len(filtered))
    c2.metric(
        "Average score",
        round(filtered["opportunity_score"].mean(), 2) if len(filtered) else 0,
    )
    c3.metric(
        "Max score",
        int(filtered["opportunity_score"].max()) if len(filtered) else 0,
    )

    display_cols = [
        "source", "document_number", "title", "policy_stage",
        "industry_tags", "states", "opportunity_score",
    ]

    st.subheader("Top 10")
    st.dataframe(
        filtered.sort_values("opportunity_score", ascending=False).head(10)[display_cols],
        use_container_width=True,
    )

    st.subheader("All filtered opportunities")
    st.dataframe(
        filtered.sort_values("opportunity_score", ascending=False)[display_cols],
        use_container_width=True,
    )

    st.subheader("Distributions")
    c4, c5 = st.columns(2)
    with c4:
        st.write("By source")
        st.bar_chart(filtered["source"].value_counts())
    with c5:
        st.write("By policy stage")
        st.bar_chart(filtered["policy_stage"].value_counts())

    st.write("Score distribution")
    st.bar_chart(filtered["opportunity_score"].value_counts().sort_index())
