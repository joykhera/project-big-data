import sys
import pandas as pd
from src.exception import CustomException
from typing import List
INDUSTRY_KEYWORDS = {
    "energy": ["energy", "solar", "wind", "electricity", "power"],
    "healthcare": ["health", "hospital", "cdc", "medical"],
    "transportation": ["transport", "rail", "airport", "highway"],
    "housing": ["housing", "real estate", "rent", "mortgage"],
    "environment": ["climate", "environment", "epa", "emissions"],
    "finance": ["bank", "finance", "loan", "investment"],
    "labor": ["worker", "employment", "labor", "wage"]
}


def tag_industries(text:str) -> List:

    """ This function finds keywords in the data and put them in tags """

    try:
        text = str(text).lower().strip()
        tags = []

        for industry,keywords in INDUSTRY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    tags.append(industry)
                    break
        return tags
                
    except Exception as e:
        raise CustomException(e,sys)
    

def apply_industry_tags(df:pd.DataFrame) -> pd.DataFrame:

    """ This function applies tags on text column in the dataset """


    try:
        df["industry_tags"] = df["text"].apply(tag_industries)
        return df 
    except Exception as e:
        raise CustomException(e,sys)