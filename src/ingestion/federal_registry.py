import requests
from src.utils.file_utils import save_to_json
from src.logger import logging
from src.exception import CustomException
import sys

BASE_URL = "https://www.federalregister.gov/api/v1/documents.json"

def fetch_federal_register(per_page:int = 10) -> dict:

    logging.info("Fetch data from federal register")

    """
    This function fecth most recent documents from Federal Register API

    input argument : Number of documents to request

    output : API response as a dictionary  

    """
    try:
     params = {
         "per_page": per_page
        }

     response = requests.get(BASE_URL, params=params, timeout= 30)
     response.raise_for_status()

     return response.json()
    except Exception as e:
       raise CustomException(e,sys)


def main():
    data = fetch_federal_register(per_page=100)
    documents = data.get("results",[])
    save_data = save_to_json(data,file_name_prefix='federal_registry')
    
    
    

if __name__ == "__main__":
    main()