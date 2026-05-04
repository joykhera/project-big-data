import os
import sys
import json
import pandas as pd
from src.exception import CustomException
from typing import List
from src.utils.file_utils import load_json
from src.utils.file_utils import save_csv
from src.processing.feature_engineering import apply_all_features
from src.processing.tagging import apply_industry_tags
from src.processing.geography import apply_geography
from src.processing.scoring import apply_opportunity_score
from src.paths import get_project_root


def extract_documents(data:dict) -> List:
    """
    This function extracts results from the file
    """
    try:
     return data.get('results',[])
    
    except Exception as e:
       raise CustomException(e, sys)
    

def transform_documents(documents:List) -> pd.DataFrame:
   rows = []

   try:
      for doc in documents:
         row = {
            "document_number": doc.get("document_number"),
            "title": doc.get("title"),
            "type": doc.get("type"),
            "publication_date": doc.get("publication_date"),
            "abstract": doc.get("abstract"),
            "agency_names": ", ".join(
                [agency.get("name", "") for agency in doc.get("agencies", [])]
            ),
            "agencies_full": json.dumps(doc.get("agencies", [])),
            "html_url": doc.get("html_url"),
            "pdf_url": doc.get("pdf_url"),
            "public_inspection_pdf_url": doc.get("public_inspection_pdf_url"),        
         }
         rows.append(row)

      return pd.DataFrame(rows)
      
   except Exception as e:
      raise CustomException(e,sys)
    
def main():
    try:
        root = get_project_root()
        input_path = root / "data/raw_data/federal_registry_2026-03-31_10:15:42.json"
        output_path = root / "data/processed/federal_register_documents.csv"

        data = load_json(str(input_path))
        documents = extract_documents(data)
        df = transform_documents(documents)
        df = apply_all_features(df,source_name="federal_register")
        df = apply_industry_tags(df)
        df = apply_geography(df)
        df = apply_opportunity_score(df)
        save_csv(df, str(output_path))
        print(
         df.sort_values("opportunity_score", ascending=False)[
        ["document_number", "title", "policy_stage", "industry_tags", "states", "opportunity_score"]
         ].head(20)
)

        
    except Exception as e:
       raise CustomException(e,sys)


if __name__ == "__main__":
    main()