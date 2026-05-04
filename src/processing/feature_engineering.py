import sys
import pandas as pd
from src.exception import CustomException

def add_source(df:pd.DataFrame, source_name:str) -> pd.DataFrame:
    """ This function add the source column """
    try:
        df["source"] = source_name
        return df
    except Exception as e:
        raise CustomException(e,sys)
    
def add_text_column(df:pd.DataFrame) -> pd.DataFrame:
    """ This function combines title and abstract """
    try:
        df["text"] = df["title"].fillna("") + " " + df["abstract"].fillna("")
        return df
    except Exception as e:
        raise CustomException(e,sys)
    
def add_has_abstract(df:pd.DataFrame) -> pd.DataFrame:
    """ This function returns True if there is a abstract """
    try:
        df["has_abstract"] = df["abstract"].notna()
        return df
    except Exception as e:
        raise CustomException(e,sys)

def add_title_length(df:pd.DataFrame) -> pd.DataFrame:
    """ This function count the length of the title """
    try:
        df["title_length"] = df["title"].fillna("").str.len()
        return df
    except Exception as e:
        raise CustomException(e,sys)
    
def add_abstract_length(df: pd.DataFrame) -> pd.DataFrame:
    """ This function count the length of the abstract"""
    try:
        df["abstract_length"] = df["abstract"].fillna("").str.len()
        return df
    except Exception as e:
        raise CustomException(e,sys)

def add_agency_count(df: pd.DataFrame) -> pd.DataFrame:
    """ This function count the number of agencies """
    try:
        df["agency_count"] = df["agency_names"].fillna("").apply(
            lambda x: len([name for name in x.split(",") if name.strip() != ""])
        )
        return df
    except Exception as e:
        raise CustomException(e,sys)


def add_policy_stage(df: pd.DataFrame) -> pd.DataFrame:
    """ This function rename type to policy_stage"""
    try:
        df["policy_stage"] = df["type"].fillna("unknown")
        return df
    except Exception as e:
        raise CustomException(e,sys)


def apply_all_features(df: pd.DataFrame,source_name:str) -> pd.DataFrame:

    """ This combine all the functions """

    try:
     df = add_source(df,source_name)
     df = add_text_column(df)
     df = add_has_abstract(df)
     df = add_title_length(df)
     df = add_abstract_length(df)
     df = add_agency_count(df)
     df = add_policy_stage(df)
     return df
    except Exception as e:
        raise CustomException(e,sys)