#this runs the entire pipeline in one swoop
from data_ingestion.extractor import DataExtractor
from data_ingestion.datalake_loader import AzureBlobHandler

if __name__ == "__main__":
    # step 1 — extract
    print("=== EXTRACTING ===")
    with DataExtractor() as extractor:
        df = extractor.fetch_data(
            limit=10000,
            since_date="2025-01-01" 
        )
    print(f"Got {len(df)} rows\n")

    # step 2 - Load
    print("=== Loading into Datalake ===")
    with AzureBlobHandler(df) as blob_handler:
        blob_handler.data_uploader()

    # step 3 - reviewing tables

    