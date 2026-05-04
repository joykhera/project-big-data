from datetime import datetime

import pandas as pd
import streamlit as st
from src.paper_tool.analyzer import clean_text, extract_key_points, top_keywords
from src.paper_tool.arxiv_client import download_pdf_bytes, search_arxiv_papers
from src.paper_tool.opportunity_engine import generate_opportunities
from src.paper_tool.pdf_tools import extract_text_from_pdf
from src.paper_tool.storage import (
    append_history,
    export_csv_bytes,
    load_history,
    opportunities_to_dataframe,
)


def _paper_source_panel() -> tuple[str, str, str]:
    st.subheader("1) Select Paper Source")
    mode = st.radio("Source", ["Upload PDF", "Search arXiv"], horizontal=True)

    paper_title = ""
    paper_text = ""

    if mode == "Upload PDF":
        uploaded = st.file_uploader("Upload research paper (PDF)", type=["pdf"])
        if uploaded is not None:
            paper_title = uploaded.name
            with st.spinner("Extracting text from PDF..."):
                paper_text = extract_text_from_pdf(uploaded.getvalue())
            st.success("PDF loaded successfully.")
        return mode, paper_title, paper_text

    query = st.text_input("arXiv topic", value="ai healthcare")
    col1, col2 = st.columns([1, 1])
    with col1:
        search_clicked = st.button("Search papers")
    with col2:
        parse_pdf_mode = st.checkbox("Try full PDF parse", value=False)

    if search_clicked:
        try:
            st.session_state["arxiv_results"] = search_arxiv_papers(query, max_results=8)
        except Exception as exc:
            st.error(f"Search failed: {exc}")

    results = st.session_state.get("arxiv_results", [])
    if not results:
        return mode, paper_title, paper_text

    options = {f"{idx + 1}. {item['title']}": item for idx, item in enumerate(results)}
    selected_key = st.selectbox("Pick one paper", list(options.keys()))
    selected = options[selected_key]
    paper_title = selected["title"]
    st.markdown(f"[Open paper page]({selected['paper_link']})")

    if parse_pdf_mode and selected["pdf_link"]:
        if st.button("Load selected PDF"):
            try:
                with st.spinner("Downloading and parsing PDF..."):
                    pdf_bytes = download_pdf_bytes(selected["pdf_link"])
                    paper_text = extract_text_from_pdf(pdf_bytes)
                st.success("Loaded full paper text from PDF.")
            except Exception as exc:
                st.warning(f"PDF parsing failed. Falling back to abstract. ({exc})")
                paper_text = clean_text(selected["summary"])
    else:
        paper_text = clean_text(selected["summary"])
        st.info("Using abstract text (faster mode).")

    return mode, paper_title, paper_text


def _analysis_panel(paper_text: str) -> tuple[list[tuple[str, int]], list[str]]:
    st.subheader("2) Extract Insights")
    keywords = top_keywords(paper_text, top_n=20)
    points = extract_key_points(paper_text, limit=8)

    col1, col2, col3 = st.columns(3)
    col1.metric("Extracted words", len(paper_text.split()))
    col2.metric("Keywords", len(keywords))
    col3.metric("Key points", len(points))

    st.markdown("**Text preview**")
    st.write(paper_text[:1400] + ("..." if len(paper_text) > 1400 else ""))

    if keywords:
        df = pd.DataFrame(keywords, columns=["keyword", "count"])
        st.markdown("**Top keywords**")
        st.bar_chart(df.set_index("keyword")["count"].head(12))
    else:
        st.warning("No keywords detected.")

    st.markdown("**Key points**")
    if points:
        for idx, point in enumerate(points, start=1):
            st.markdown(f"**{idx}.** {point}")
    else:
        st.info("No key points extracted.")

    return keywords, points


def _opportunity_panel(
    source_mode: str,
    paper_title: str,
    keywords: list[tuple[str, int]],
    points: list[str],
) -> None:
    st.subheader("3) Generate Business Opportunities")
    count = st.slider("How many opportunities?", min_value=3, max_value=10, value=6)
    min_score = st.slider("Minimum score filter", min_value=50, max_value=95, value=60)

    if st.button("Generate opportunity board", type="primary"):
        opportunities = generate_opportunities(keywords, points, count=count)
        if not opportunities:
            st.warning("Not enough data to generate opportunities.")
            return

        df = opportunities_to_dataframe(opportunities)
        filtered = df[df["score"] >= min_score].sort_values("score", ascending=False)
        st.session_state["generated_opportunities"] = filtered

    generated = st.session_state.get("generated_opportunities")
    if generated is None or generated.empty:
        return

    st.dataframe(generated, use_container_width=True, hide_index=True)
    for idx, row in generated.iterrows():
        with st.expander(f"{idx + 1}. {row['title']} (score: {row['score']})"):
            st.markdown(f"**Target user:** {row['target_user']}")
            st.markdown(f"**Problem:** {row['problem_statement']}")
            st.markdown(f"**Solution:** {row['solution_outline']}")
            st.markdown(f"**Revenue model:** {row['revenue_model']}")
            st.markdown(f"**MVP scope:** {row['mvp_scope']}")
            st.markdown(f"**Risk:** {row['risk_note']}")

    st.download_button(
        "Download opportunities CSV",
        data=export_csv_bytes(generated),
        file_name="generated_opportunities.csv",
        mime="text/csv",
    )

    if st.button("Save this run to history"):
        append_history(
            paper_title=paper_title or "Unknown paper",
            source=source_mode,
            opportunities=generated.to_dict(orient="records"),
        )
        st.success("Saved to history.")


def _history_panel() -> None:
    st.subheader("4) Saved Runs")
    history_df = load_history()
    if history_df.empty:
        st.info("No saved runs yet.")
        return
    st.dataframe(history_df.sort_values("run_time", ascending=False), use_container_width=True)


def render_paper_tool() -> None:
    st.title("Research Paper -> Business Opportunity Tool")
    st.caption(
        "Submission-ready workflow: search or upload paper, extract insights, generate scored opportunities,"
        " and export report."
    )

    source_mode, paper_title, paper_text = _paper_source_panel()
    if paper_text:
        keywords, points = _analysis_panel(paper_text)
        _opportunity_panel(source_mode, paper_title, keywords, points)
    st.divider()
    _history_panel()
    st.caption(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


def main() -> None:
    st.set_page_config(page_title="Paper to Opportunity - Complete MVP", layout="wide")
    render_paper_tool()


if __name__ == "__main__":
    main()
