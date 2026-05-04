# Research Paper to Business Opportunity - MVP

This project helps a student:

1. Find a research paper (`Upload PDF` or `Search arXiv`)
2. Extract key insights
3. Generate practical business opportunities with a simple score
4. Export opportunities as CSV
5. Save each run into local history

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Core workflow

- **Input source**
  - Upload a PDF file
  - Search arXiv by topic keyword
- **Insight extraction**
  - Top keywords
  - Key points from paper text
- **Opportunity board**
  - Opportunity title
  - Target users
  - Problem and solution
  - Revenue model
  - MVP plan and risk note
  - Score filter
- **Output**
  - Download CSV
  - Save history to `data/processed/paper_opportunity_history.csv`

