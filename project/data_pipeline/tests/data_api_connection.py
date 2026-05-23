#use this for testing connection to data api
import os
import pandas as pd
from dotenv import load_dotenv
from sodapy import Socrata


if __name__ == "__main__":
    
    #loads environment variables from .env file
    load_dotenv()

    try: 
        # Create a Socrata client
        client = Socrata(os.getenv("DATA_URL"), None)

        response = client.get("mmzv-x632", limit=5)
        if response:
            print("Connection Successful!")
            print(f"Sample Data: {len(response)} records retrieved.")
            print("You can go through the ELT Pipeline.")
            df = pd.DataFrame(response)
            print(df.head())
        else: 
            print("Connection made but No data returned.")
    except Exception as e:
        print(f"Connection Failed: {e}")
        print("Please check your API URL in the .env file and try again.")
