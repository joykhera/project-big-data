import json
import os 
from datetime import datetime
from src.exception import CustomException
import sys
import pandas as pd


def save_to_json(data, folder = 'data/raw_data', file_name_prefix ='file_name'):
    """
    This function saves fetched raw data in the data folder
    input -> data : fetched data, folder:data/raw_data and file_name_prefix:file_name
    output -> json file in the given location 
    """

    try:
     os.makedirs(folder,exist_ok=True) # Create the file 

     timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
     file_path = os.path.join(folder,f"{file_name_prefix}_{timestamp}.json")

     with open(file_path,'w') as f:
         json.dump(data,f,indent=4)
    
     print(f" file saved to : {file_path}")
    except Exception as e:
       raise CustomException(e,sys)


def load_json(file_path:str) -> dict:
   """
   Load json files from the disk. 
   """
   try:
    with open(file_path, 'r') as f:
          return json.load(f)
    print("json file loaded")
   except Exception as e:
      raise CustomException(e,sys)
   

def save_csv(df:pd.DataFrame,output_path:str) -> None:
   """
   This function is resposible for saving the csv file to the 
   given output path
   """
   try:
      os.makedirs(os.path.dirname(output_path),exist_ok=True)
      df.to_csv(output_path,index=False)
      print(f"saved processed file to {output_path}")
   except Exception as e:
      raise CustomException(e,sys)
   

