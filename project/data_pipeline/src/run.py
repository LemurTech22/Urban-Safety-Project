"""Run the urban safety pipeline end to end."""
import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv
from data_ingestion.extractor import DataExtractor
from data_ingestion.datalake_loader import AzureBlobHandler
from data_transformation.schema_validation import schema
from data_transformation.transformation import Transformation
from data_visualization.Visualization import Visualization


BASE_DIR = Path(__file__).resolve().parents[2]
DUCKDB_PATH = BASE_DIR / "data.duckdb"


load_dotenv()
if __name__ == "__main__":
    # step 1 — extract
    print("Extracting Data from API \n Please Wait ...")
    with DataExtractor() as extractor:
        df = extractor.fetch_data(
            limit=10000,
            since_date="2025-01-01" 
        )
    print(f"Got {len(df)} rows\n")

    # step 2 - Load
    print("[2/5] Loading Data into Cloud \n Please Wait ...")
    with AzureBlobHandler(df) as blob_handler:
        blob_handler.data_uploader()

    # step 3 - reviewing tables
    print("[3/5] Validating Schema \n Please Wait...")
    try:
        schema.validate(df, lazy=True)
        print("Schema Passed Validation")
    except Exception as e:
            print(f" Schema Validation Failed: {e}")

    # step 4 - transform data
    print("[4/5] Transforming data \n Please Wait ...")

    transform_df = Transformation(df)
    silver_df = transform_df.transform_to_silver()
    
    container_silver = os.getenv("AZURE_CONTAINER_SILVER", "silver")
    silver_path = (
        f"urban_crash/"
        f"year={__import__('datetime').datetime.utcnow().year}/"
        f"month={__import__('datetime').datetime.utcnow().month:02d}/"
        f"day={__import__('datetime').datetime.utcnow().day:02d}/"
        f"clean.csv"
    )
    
    with AzureBlobHandler(silver_df) as handler:
        handler.upload_df(
            silver_df,
            container=container_silver,
            blob_path=silver_path
        )

    print("[5/5] Uploading Transformed data into Azure \nPlease Wait ...")
    
    conn = duckdb.connect(str(DUCKDB_PATH))
    gold_df = conn.execute("SELECT * FROM mart_crash_hotspot").df()
    conn.close()
    
    container_gold = os.getenv("AZURE_CONTAINER_GOLD", "gold")
    gold_path = (
        f"urban_crash/"
        f"year={__import__('datetime').datetime.utcnow().year}/"
        f"month={__import__('datetime').datetime.utcnow().month:02d}/"
        f"day={__import__('datetime').datetime.utcnow().day:02d}/"
        f"clean.csv"
    )
    with AzureBlobHandler(gold_df) as handler:
        handler.upload_df(
            gold_df,
            container=container_gold,
            blob_path=gold_path
        )

    print("[5/5] Upload Complete")

    value = input("Would you like to view plots & Interactive Map?")

    if value.lower() == 'y':
        print(f"Data Transformed Commencing Visualizations")
        print(gold_df.columns.tolist())
        print("\n[5/5] Visualizations Beginning \n Please Wait ...")

        with Visualization(gold_df) as Visualization:
            Visualization.generate_visuals()
            
    else: 
         print("Ending Pipeline \nThank you for using the pipeline.")
