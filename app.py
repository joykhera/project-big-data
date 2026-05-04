import streamlit as st

from mvp_app import render_paper_tool
from src.policy_dashboard import render_policy_dashboard


def main() -> None:
    st.set_page_config(page_title="Project Big Data", layout="wide")
    module = st.sidebar.radio(
        "Select module",
        ["Research Paper Opportunity Tool", "Policy Opportunity Dashboard"],
    )

    if module == "Research Paper Opportunity Tool":
        render_paper_tool()
    else:
        render_policy_dashboard()


if __name__ == "__main__":
    main()

