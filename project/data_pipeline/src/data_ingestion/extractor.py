import os 
import pandas as pd
from dotenv import load_dotenv
from sodapy import Socrata

class DataExtractor: 
    def __init__(self):
        load_dotenv()
        self.data_url= os.getenv("DATA_URL",None)
        self.dataset_id = os.getenv("DATASET_ID")
        self.app_token= os.getenv("SOCRATA_APP_TOKEN", None)
        self.client=None

    #sets up the api environment 
    def __enter__(self):
        self.client = Socrata(self.data_url, self.app_token)
        return self
    #releases any resources from the session.
    def __exit__(self,exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()

    def fetch_data(self, limit: int=10000, since_date: str=None)-> pd.DataFrame:
        params = {
        "limit": limit,
        "order": "crash_date_time DESC",
        }

        if since_date:
            params["where"] = f"crash_date_time >= '{since_date}T00:00:00.000'"   
        print("Gathering data from API")
        print("Please Wait ...")

        response = self.client.get(self.dataset_id, **params)

        if not response:
            raise ValueError("API returned empty: \nCheck your .env and dataset ID ")
        
        df = pd.DataFrame(response)

        print("Extraction complete")
        print(f"Collected {len(df)} records - {len(df.columns)} columns")
        return df

#Clean up main here and run code off of run.py in the data pipeline folder
def ingestion_pipe(self):
        
    print("Running ELT ingestion pipeline")
        
    df=self.fetch_data(limit=10000, since_date="2025-01-01")
    print(df.shape)
    print(df.dtypes)
    print(df.isnull().sum())
