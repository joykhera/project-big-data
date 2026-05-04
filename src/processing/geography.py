import sys
from typing import List
import pandas as pd
from src.exception import CustomException




US_STATES = [
    "Alabama", "AL", "Alaska", "AK", "Arizona", "AZ", "Arkansas", "AR", "California", "CA", 
    "Colorado", "CO", "Connecticut", "CT", "Delaware", "DE", "Florida", "FL", "Georgia", "GA", 
    "Hawaii", "HI", "Idaho", "ID", "Illinois", "IL", "Indiana", "IN", "Iowa", "IA", "Kansas", "KS", 
    "Kentucky", "KY", "Louisiana", "LA", "Maine", "ME", "Maryland", "MD", "Massachusetts", "MA", 
    "Michigan", "MI", "Minnesota", "MN", "Mississippi", "MS", "Missouri", "MO", "Montana", "MT", 
    "Nebraska", "NE", "Nevada", "NV", "New Hampshire", "NH", "New Jersey", "NJ", "New Mexico", "NM", 
    "New York", "NY", "North Carolina", "NC", "North Dakota", "ND", "Ohio", "OH", "Oklahoma", "OK", 
    "Oregon", "OR", "Pennsylvania", "PA", "Rhode Island", "RI", "South Carolina", "SC", "South Dakota", "SD", 
    "Tennessee", "TN", "Texas", "TX", "Utah", "UT", "Vermont", "VT", "Virginia", "VA", "Washington", "WA", 
    "West Virginia", "WV", "Wisconsin", "WI", "Wyoming", "WY"

]

def extract_state(text:str) -> List:

    """ This function is resposible of finding the state mentioned in the documents. """

    try:
        text = str(text).lower().strip()
        states_found = []

        for state in US_STATES:
            if state in text:
                states_found.append()
        
        return states_found
    
    except Exception as e:
        raise CustomException(e,sys)
    

def apply_geography(df:pd.DataFrame) -> pd.DataFrame:
    """ This function creates a new column in dataset and apply extract_state 
    to find the state that involve in policy changes. """

    df["states"] = df["text"].apply(extract_state)
    return df