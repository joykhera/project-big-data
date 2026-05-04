# Project Big Data

A Streamlit MVP that turns two kinds of public data into scored business opportunities:

1. **Research papers** — search arXiv or upload a PDF, extract keywords + key points, and generate distinct, paper-specific business opportunities (target user, problem, solution, revenue model, MVP plan, score).
2. **Federal policy documents** — ingest Federal Register rules and Congress.gov bills, score them across policy stage, industry, geography, and text richness, and explore the top opportunities in a filterable dashboard.

## Quickstart

```bash
python -m venv venv
source venv/bin/activate         # on macOS / Linux
pip install -e ".[dev]"
cp .env.example .env             # add your GOOGLE_AI_API_KEY (optional but recommended)
streamlit run app.py
```

The app opens with a sidebar that switches between the two modules.

## Architecture

```
app.py                                 Streamlit entry point
src/project_big_data/
  config.py                            paths, env vars, model identifiers
  logging_setup.py                     single rotating log file
  paper_tool/
    arxiv_client.py                    arxiv lib wrapper (rate-limited, retries)
    pdf_tools.py                       PyMuPDF text extraction
    analysis.py                        YAKE keywords + sumy LexRank key points
    opportunities.py                   Google Gemini (with template fallback)
    storage.py                         history CSV (append-only)
    ui.py                              Streamlit panels for the paper flow
  policy/
    ingestion/
      federal_register.py              Federal Register API
      congress.py                      Congress.gov API
      _io.py                           filesystem-safe JSON / CSV helpers
    processing/
      features.py                      shared feature engineering
      tagging.py                       industry keyword tagging
      geography.py                     U.S. state extraction (regex, word-boundary)
      scoring.py                       composite opportunity score
    pipeline.py                        ingest -> process -> top_opportunities.csv
    ui.py                              dashboard with filters
tests/                                 pytest suite (36 tests)
data/
  raw_data/                            (gitignored) downloaded JSON dumps
  processed/                           cleaned + scored CSVs
```

## Library choices

| Job | Library | Why |
|---|---|---|
| arXiv search | [`arxiv`](https://github.com/lukasschwab/arxiv.py) | Built-in rate limiting per arXiv ToS, retries, pagination. |
| PDF parsing | [`pymupdf`](https://pymupdf.readthedocs.io/) | Wins benchmarks for word-order accuracy on scientific PDFs. |
| Keywords | [`yake`](https://github.com/LIAAD/yake) | Unsupervised, single-document, no model download. |
| Key points | [`sumy`](https://github.com/miso-belica/sumy) (LexRank) | Extractive summarization without an LLM. |
| Opportunity generation | [`google-genai`](https://github.com/googleapis/python-genai) (Gemini) | JSON-mode structured output for distinct, paper-specific opportunities; falls back to varied templates if no key set. |

## Running the policy pipeline

The dashboard reads `data/processed/top_opportunities.csv`. Regenerate it from the latest raw dumps:

```bash
# Fetch fresh raw data (requires CONGRESS_API_KEY for the Congress feed)
python -m project_big_data.policy.ingestion.federal_register
python -m project_big_data.policy.ingestion.congress

# Process and score everything; writes top_opportunities.csv
python -m project_big_data.policy.pipeline
# or, after `pip install -e .`:
pbd-policy-pipeline --min-score 5
```

`--skip-fed` and `--skip-congress` let you re-run partial pipelines.

## Tests

```bash
pytest                  # 36 tests, ~2s
pytest --cov=project_big_data
```

## Notable bug fixes vs. the original MVP

- `geography.extract_state` no longer calls `list.append()` with no argument (the old version always returned `[]`, so `geography_score` was always 0).
- The dashboard's industry filter now does substring/membership matching against the parsed tag list instead of `isin` against comma-separated strings (which never matched).
- Logger no longer creates one timestamped *directory* per import; rotates a single `logs/app.log`.
- Filenames written to `data/raw_data/` use `-` separators instead of `:` (which broke macOS Finder and some shell tools).
- Removed the `CustomException` shim that was wrapping every function — native exceptions propagate with full tracebacks now.
