import os
import io
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

#idea maybe create a template so that other sources can use it like silver and gold layer.

class AzureBlobHandler:
    #initialize variables and .envs
    def __init__(self, df: pd.DataFrame):
        load_dotenv()
        self.storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
        self.tenant_id       = os.getenv("AZURE_TENANT_ID")
        self.client_id       = os.getenv("AZURE_CLIENT_ID")
        self.client_secret   = os.getenv("AZURE_CLIENT_SECRET")
        self.bronze          = os.getenv("AZURE_CONTAINER_BRONZE")
        self.credential      = None
        self.blob_client     = None
        self.df              = df

        missing = [
            k for k, v in {
                "AZURE_STORAGE_ACCOUNT": self.storage_account,
                "AZURE_TENANT_ID":       self.tenant_id,
                "AZURE_CLIENT_ID":       self.client_id,
                "AZURE_CLIENT_SECRET":   self.client_secret,
            }.items() if not v
        ]
        
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {missing}\n"
                f"Check your .env file."
            )
    #runs first using the with statement in run.py
    #intializes variables for us to use. ensures setup and tear down are consistent
    #similar to try statements
    def __enter__(self):
        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        self.blob_client = BlobServiceClient(
            f"https://{self.storage_account}.blob.core.windows.net/",
            credential=self.credential
        )
        return self
    
    #releases resources once pipeline is finished
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.blob_client:              
            self.blob_client.close()
        if self.credential:
            self.credential.close()

    #grabs the dataframe and uploads to the cloud aka azure
    def upload_df(
        self,
        df: pd.DataFrame,
        container: str,
        blob_path: str,
        file_format: str = "csv"
    ):
        
        buffer = io.BytesIO()
        if file_format == "parquet":
            df.to_parquet(buffer, index=False, engine="pyarrow")
        else:
            df.to_csv(buffer, index=False, encoding="utf-8")

        buffer.seek(0)

        #initializes the azure client
        container_client = self.blob_client.get_container_client(container)

        #uploads the df
        container_client.upload_blob(
            name=blob_path,
            data=buffer,
            overwrite=True
        )

        size_kb = buffer.tell() / 1024
        print(f"  ✓ Uploaded {len(df)} rows ({size_kb:.1f} KB) "
              f"→ {container}/{blob_path}")

    def file_exists(self, container: str, blob_path: str) -> bool:

        container_client = self.blob_client.get_container_client(container)
        blob_client = container_client.get_blob_client(blob_path)
        return blob_client.exists()

    def list_files(self, container: str, prefix: str = "") -> list[str]:

        container_client = self.blob_client.get_container_client(container)
        blobs = container_client.list_blobs(name_starts_with=prefix)
        return [b["name"] for b in blobs]
    
    def data_verification(self,blob_path: str):

        print("\n=== VERIFYING BRONZE ===")
        files = self.list_files(self.bronze, prefix="urban_crash/")
        print(f"Files in bronze/urban_crash/:")
        for f in files:
            print(f"  {f}")

        if self.file_exists(self.bronze, blob_path):
            print(f"\n✓ Verified — {blob_path} exists in bronze")
        else:
            print(f"\n✗ Verification failed — file not found")
    
    #this function does all the work
    def data_uploader(self):
        
        # step 2 — upload to bronze
        #Upload layer function
        print("=== UPLOADING TO BRONZE ===")
        blob_path = build_bronze_path("urban_crash")

        if self.file_exists(self.bronze, blob_path):
            print(f"Already exists at {blob_path} — skipping")
        else:
            self.upload_df(self.df, container=self.bronze, blob_path=blob_path)

        self.data_verification(blob_path)
            # step 3 — verify
            #Split into verification function
        
def build_bronze_path(dataset_name: str) -> str:
    now = datetime.utcnow()
    return (
        f"{dataset_name}/"
        f"year_{now.year}/"
        f"month_{now.month:02d}/"
        f"day_{now.day:02d}/"
        f"raw.csv"
    )
    