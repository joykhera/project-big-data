import sys
from pathlib import Path

import pandas as pd

from src.exception import CustomException

_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    try:
        df = pd.read_csv(_ROOT / "data/processed/conmbined_data.csv")
        print(df)

        print("__________Head__________\n")
        print(df.head())
        print(" \n")

        print("__________Tail__________\n")
        print(df.tail())
        print(" \n")

        print("__________Random__________\n")
        print(df.sample(n=5))
        print(" \n")

        print(f"size of the dataset : {df.size}")
        print(f"shape of the dataset : {df.shape}")
        print(f"columns of the dataset : {df.columns} ")
        print(" \n")

        print("__________Summary__________\n")
        df.info()
        print(" \n")

        print("__________Source Count__________\n")
        print(df["source"].value_counts())

        print("\n__________Top 20 Opportunities__________")
        top_df = df.sort_values("opportunity_score", ascending=False, ignore_index=True)
        print(
            top_df[
                [
                    "source",
                    "document_number",
                    "title",
                    "policy_stage",
                    "industry_tags",
                    "states",
                    "opportunity_score",
                ]
            ].head(20)
        )

        print("\n__________Industry Distribution__________")
        print(df["industry_tags"].astype(str).value_counts().head(10))

        print("\n__________State Distribution__________")
        print(df["states"].astype(str).value_counts().head(20))

        top_df[top_df["opportunity_score"] >= 5].to_csv(
            path_or_buf=_ROOT / "data/processed/top_opportunities.csv",
            index=False,
        )
    except Exception as e:
        raise CustomException(e, sys)


if __name__ == "__main__":
    main()

