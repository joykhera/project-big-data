from pathlib import Path

import pandas as pd
import streamlit as st


def render_policy_dashboard() -> None:
    st.title("Policy Opportunity Dashboard")
    st.write("Analyze policy-driven business and real-estate opportunities from government data.")

    csv_path = Path(__file__).resolve().parent.parent / "data/processed/top_opportunities.csv"
    if not csv_path.exists():
        st.error("`data/processed/top_opportunities.csv` not found.")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        st.warning("Opportunity data is empty.")
        return

    st.sidebar.header("Filters")
    source_options = sorted(df["source"].dropna().unique())
    selected_sources = st.sidebar.multiselect("Select Source", options=source_options, default=source_options)

    policy_stage_options = sorted(df["policy_stage"].dropna().unique())
    selected_policy_stages = st.sidebar.multiselect(
        "Select Policy Stage",
        options=policy_stage_options,
        default=policy_stage_options,
    )

    min_score = st.sidebar.slider(
        "Minimum Opportunity Score",
        min_value=int(df["opportunity_score"].min()),
        max_value=int(df["opportunity_score"].max()),
        value=int(df["opportunity_score"].min()),
    )
    search_term = st.sidebar.text_input("Search title")

    df["industry_tags"] = df["industry_tags"].fillna("").astype(str)
    df["states"] = df["states"].fillna("").astype(str)
    industry_options = sorted([x for x in df["industry_tags"].unique() if x.strip() != ""])
    selected_industries = st.sidebar.multiselect("Select Industry Tags", options=industry_options, default=[])

    filtered_df = df[
        (df["source"].isin(selected_sources))
        & (df["policy_stage"].isin(selected_policy_stages))
        & (df["opportunity_score"] >= min_score)
    ]

    if search_term.strip():
        filtered_df = filtered_df[filtered_df["title"].str.contains(search_term, case=False, na=False)]

    if selected_industries:
        filtered_df = filtered_df[filtered_df["industry_tags"].isin(selected_industries)]

    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Opportunities", len(filtered_df))
    col2.metric("Average Score", round(filtered_df["opportunity_score"].mean(), 2) if len(filtered_df) > 0 else 0)
    col3.metric("Max Score", int(filtered_df["opportunity_score"].max()) if len(filtered_df) > 0 else 0)

    st.subheader("Top 10 Opportunities")
    top_10 = filtered_df.sort_values("opportunity_score", ascending=False).head(10)
    st.dataframe(
        top_10[
            [
                "source",
                "document_number",
                "title",
                "policy_stage",
                "industry_tags",
                "states",
                "opportunity_score",
            ]
        ],
        use_container_width=True,
    )

    st.subheader("All Filtered Opportunities")
    st.dataframe(
        filtered_df.sort_values("opportunity_score", ascending=False)[
            [
                "source",
                "document_number",
                "title",
                "policy_stage",
                "industry_tags",
                "states",
                "opportunity_score",
            ]
        ],
        use_container_width=True,
    )

    st.subheader("Charts")
    col4, col5 = st.columns(2)
    with col4:
        st.write("Source Distribution")
        st.bar_chart(filtered_df["source"].value_counts())
    with col5:
        st.write("Policy Stage Distribution")
        st.bar_chart(filtered_df["policy_stage"].value_counts())

    st.subheader("Opportunity Score Distribution")
    st.bar_chart(filtered_df["opportunity_score"].value_counts().sort_index())

