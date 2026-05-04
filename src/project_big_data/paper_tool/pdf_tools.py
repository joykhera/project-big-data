"""PDF text extraction via PyMuPDF (fitz). Benchmarks consistently show better
word-order preservation and accuracy on scientific PDFs than pypdf."""

from __future__ import annotations

import pymupdf


def extract_text_from_pdf(file_bytes: bytes) -> str:
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        pages = [page.get_text("text") for page in doc]
    return "\n".join(pages).strip()
