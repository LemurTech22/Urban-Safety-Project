# data_pipeline/src/data_ingestion/inspect_fields.py
# run once — never needs to run again after you build your schema

import os
import sys
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from extractor import DataExtractor

if __name__ == "__main__":

    with DataExtractor() as extractor:
        df = extractor.fetch_data(limit=5)

    print("=" * 60)
    print(f"COLUMNS ({len(df.columns)} total)")
    print("=" * 60)
    for col in df.columns:
        sample_val = df[col].iloc[0] if len(df) > 0 else "N/A"
        print(f"  {col:<35} → {str(sample_val)[:40]}")

    print("\n" + "=" * 60)
    print("DTYPES")
    print("=" * 60)
    print(df.dtypes)

    print("\n" + "=" * 60)
    print("NULL COUNTS")
    print("=" * 60)
    print(df.isnull().sum())

    print("\n" + "=" * 60)
    print("SAMPLE ROW (full)")
    print("=" * 60)
    print(df.iloc[0].to_dict())
    