import requests
import sys
import os
from dotenv import load_dotenv
from src.exception import CustomException
from src.utils.file_utils import save_to_json


load_dotenv()

BASE_URL = "https://api.congress.gov/v3/bill"
API_KEY = os.getenv("CONGRESS_API_KEY")

def fetch_congress_bills(limit:int = 50) -> dict:
    " fetch recent bills from Congress.gov API"

    try:
        params = {
            "api_key" : API_KEY,
            "limit" : limit,
            "format" : "json"
        }
        response = requests.get(BASE_URL, params=params, timeout= 30)
        response.raise_for_status()

        return response.json()
    except Exception as e:
       raise CustomException(e,sys)

def main():
    data = fetch_congress_bills(limit=100)
    documents = data.get("bills",[])
    save_data = save_to_json(data,file_name_prefix='congress_bills')
    
    
    
    

if __name__ == "__main__":
    main()