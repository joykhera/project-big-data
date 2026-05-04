import json

from project_big_data.policy import pipeline as pipe


def test_transform_federal_register():
    docs = [
        {
            "document_number": "2024-01",
            "title": "Energy rule",
            "type": "Rule",
            "publication_date": "2024-01-01",
            "abstract": "Solar power update.",
            "agencies": [{"name": "EPA"}, {"name": "DOE"}],
            "html_url": "https://example.com",
            "pdf_url": None,
            "public_inspection_pdf_url": None,
        }
    ]
    df = pipe.transform_federal_register(docs)
    assert len(df) == 1
    assert df["agency_names"].iloc[0] == "EPA, DOE"


def test_transform_congress_bills():
    bills = [
        {
            "number": "HR1",
            "title": "Healthcare bill",
            "type": "HR",
            "updateDate": "2024-02-01",
            "url": "https://example.com",
            "congress": 119,
            "originChamber": "House",
            "originChamberCode": "H",
            "latestAction": {"actionDate": "2024-02-02", "text": "Passed."},
        }
    ]
    df = pipe.transform_congress_bills(bills)
    assert df["abstract"].iloc[0] == "Passed."
    assert df["congress"].iloc[0] == 119


def test_pipeline_end_to_end_with_synthetic_raw(tmp_path, monkeypatch):
    fed_raw = {
        "results": [
            {
                "document_number": "2024-01",
                "title": "Energy rule for California",
                "type": "Rule",
                "publication_date": "2024-01-01",
                "abstract": "Solar power update " + ("x" * 200),
                "agencies": [{"name": "EPA"}],
                "html_url": "https://example.com",
                "pdf_url": None,
                "public_inspection_pdf_url": None,
            }
        ]
    }
    raw_dir = tmp_path / "raw"
    proc_dir = tmp_path / "processed"
    raw_dir.mkdir()
    proc_dir.mkdir()
    (raw_dir / "federal_registry_2024.json").write_text(json.dumps(fed_raw))

    monkeypatch.setattr(pipe, "RAW_DIR", raw_dir)
    monkeypatch.setattr(pipe, "PROCESSED_DIR", proc_dir)
    monkeypatch.setattr(pipe, "FED_REGISTER_CSV", proc_dir / "fed.csv")
    monkeypatch.setattr(pipe, "CONGRESS_CSV", proc_dir / "congress.csv")
    monkeypatch.setattr(pipe, "COMBINED_CSV", proc_dir / "combined.csv")
    monkeypatch.setattr(pipe, "TOP_CSV", proc_dir / "top.csv")

    df = pipe.run_federal_register()
    assert "opportunity_score" in df.columns
    assert df["states"].iloc[0] == ["CA"]  # geography fix from old bug

    combined = pipe.merge_and_export(min_score=0)
    assert (proc_dir / "fed.csv").exists()
    assert (proc_dir / "combined.csv").exists()
    assert (proc_dir / "top.csv").exists()
    assert len(combined) == 1
