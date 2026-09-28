from extract import fetch_submissions
from transform import transform
from load import load_to_db
from config import HANDLE

if __name__ == "__main__":
    print(f"Starting ETL Pipeline for handle: {HANDLE}")

    raw_submissions = fetch_submissions(HANDLE, count=100)
    df = transform(raw_submissions)
    load_to_db(df)