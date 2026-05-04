
import sys
import json
import pandas as pd
from typing import List
from src.exception import CustomException
from src.utils.file_utils import load_json
from src.utils.file_utils import save_csv
from src.processing.feature_engineering import apply_all_features
from src.processing.tagging import apply_industry_tags
from src.processing.geography import apply_geography
from src.processing.scoring import apply_opportunity_score
from src.paths import get_project_root


def extract_bills(data:dict) -> List:

    try:
        return data.get('bills',[])
    except Exception as e:
        raise CustomException(e,sys)
    

def transform_bills(bills:List) -> pd.DataFrame:
    rows = []
    

    try:
       for bill in bills:
           latest_action = bill.get("latestAction", {})
           row = {
                 "document_number": bill.get("number"),
                 "title": bill.get("title"),
                 "type": bill.get("type"),
                 "publication_date": bill.get("updateDate"),
                 "abstract": latest_action.get("text"),
                 "agency_names": None,
                 "agencies_full": None,
                 "html_url": bill.get("url"),
                 "pdf_url": None,
                 "public_inspection_pdf_url": None,
                 "source": "congress_bills",
                 "congress": bill.get("congress"),
                 "origin_chamber": bill.get("originChamber"),
                 "origin_chamber_code": bill.get("originChamberCode"),
                 "latest_action_date": latest_action.get("actionDate"),
                "latest_action_text": latest_action.get("text")
            }
           rows.append(row)
           
       return pd.DataFrame(rows)

    except Exception as e:
        raise CustomException(e,sys)

def main():
    try:
        root = get_project_root()
        input_path = root / "data/raw_data/congress_bills_2026-04-01_10:11:33.json"
        output_path = root / "data/processed/congress_bill_documents.csv"

        data = load_json(str(input_path))
        bills = extract_bills(data)
        df = transform_bills(bills)
        
        df = apply_all_features(df,source_name="congress_bills")
        df = apply_industry_tags(df)
        df = apply_geography(df)
        df = apply_opportunity_score(df)
        save_csv(df, str(output_path))
        print()

    except Exception as e:
        raise CustomException(e,sys)


if __name__ == "__main__":
    main()
