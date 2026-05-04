import sys
import pandas as pd
from src.exception import CustomException
from src.paths import get_project_root

def load_and_merge()->pd.DataFrame:

    try:
        root = get_project_root()
        df1 = pd.read_csv(root / "data/processed/federal_register_documents.csv")
        df2 = pd.read_csv(root / "data/processed/congress_bill_documents.csv")

        merged_df = pd.concat([df1,df2],ignore_index=True)

        return merged_df
    except Exception as e:
        raise CustomException(e,sys)

def main():

    try:
        df = load_and_merge()
        df.to_csv(get_project_root() / "data/processed/conmbined_data.csv", index=False)
    except Exception as e:
        raise CustomException(e,sys)

if __name__ == "__main__":
    main()