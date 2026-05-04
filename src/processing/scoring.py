import pandas as pd 
from typing import List

IMPORTED_TYPES = {
    "Rule" : 3,
    "Proposed Rule" : 2,
    "Notice" : 1,
    "Presidential Document" : 3
}


INDUSTRY_WEIGHTS= {
    "energy": 2,
    "healthcare": 1,
    "transportation": 2,
    "housing": 3,
    "environment": 2,
    "finance": 2,
    "labor" : 1
}

def score_policy_stage(policy_stage:str) -> int:
    """ This function assigns weights to each policy stage"""

    return IMPORTED_TYPES.get(policy_stage,0)

def score_industries(industry_tags:List) -> int:
    """ This function assigns weights to each industry tags"""
    score = 0
    for tag in industry_tags:
        score += INDUSTRY_WEIGHTS.get(tag,0)
    return score

def score_text_richness(abstract_length:int) ->int:
    if abstract_length  >=500:
        return 2
    elif abstract_length>=150:
        return 1
    else:
        return 0

def score_geography(states:str) -> int:
    if len(states) > 0:
        return 1
    else:
        return 0
    
def apply_opportunity_score(df: pd.DataFrame) -> pd.DataFrame:
    df["policy_stage_score"] = df["policy_stage"].apply(score_policy_stage)
    df["industry_score"] = df["industry_tags"].apply(score_industries)
    df["text_score"] = df["abstract_length"].apply(score_text_richness)
    df["geography_score"] = df["states"].apply(score_geography)

    df["opportunity_score"] = (
                            df["policy_stage_score"] + 
                            df["industry_score"] +
                            df["text_score"] +
                            df["geography_score"]
    )
    return df
                            

