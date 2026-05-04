"""Streamlit entry point. Run with `streamlit run app.py`."""

from __future__ import annotations

import streamlit as st

from project_big_data.paper_tool.ui import render_paper_tool
from project_big_data.policy.ui import render_policy_dashboard


def main() -> None:
    st.set_page_config(page_title="Project Big Data", layout="wide")
    module = st.sidebar.radio(
        "Module",
        ["Research Paper Opportunity Tool", "Policy Opportunity Dashboard"],
    )
    if module == "Research Paper Opportunity Tool":
        render_paper_tool()
    else:
        render_policy_dashboard()


if __name__ == "__main__":
    main()
