from extract import fetch_submissions
from transform import transform
from load import load_to_db
from config import HANDLE, COUNT

if __name__ == "__main__":
    print(f"Starting ETL Pipeline for handle: {HANDLE}, count: {COUNT}")

    raw_submissions = fetch_submissions(HANDLE, count=COUNT)
    df = transform(raw_submissions)
    load_to_db(df)