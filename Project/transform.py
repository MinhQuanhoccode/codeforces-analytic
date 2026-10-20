import pandas as pd
from extract import fetch_submissions, HANDLE   # tái sử dụng hàm Extract




def transform(submissions: list[dict]) -> pd.DataFrame:
    if not submissions: return pd.DataFrame()
    # Bước 1: list dict -> DataFrame. Mỗi dict thành 1 hàng, mỗi key thành 1 cột.
    df = pd.DataFrame(submissions)

    # Bước 2: flatten cột "problem" (đang là dict) ra các cột riêng
    # .apply(pd.Series) biến 1 cột chứa dict thành nhiều cột con

    problem_df = df["problem"].apply(pd.Series)
    df["problem_rating"] = problem_df.get("rating")   # .get() vì không phải bài nào cũng có rating
    df["problem_name"] = problem_df.get("name")

    # Bước 3: flatten "author" -> lấy handle người nộp (members là list dict)
    # dùng lambda vì cấu trúc sâu hơn 1 cấp, .apply(pd.Series) không xử lý gọn được
    df["submitter_handle"] = df["author"].apply(
        lambda a: a["members"][0]["handle"] if a.get("members") else None
    )

    # Bước 4: convert Unix timestamp -> datetime dễ đọc
    df["submit_time"] = pd.to_datetime(df["creationTimeSeconds"], unit="s")

    # Bước 5: chọn cột cần giữ, bỏ cột nested gốc (problem, author) đã lấy hết thông tin cần
    keep_cols = [
        "id", "submitter_handle", "problem_name", "problem_rating",
        "verdict", "programmingLanguage", "submit_time",
        "timeConsumedMillis", "memoryConsumedBytes",
    ]
    df = df[keep_cols]

    # Bước 6: xử lý null và duplicate
    df = df.drop_duplicates(subset="id")     # tránh insert trùng submission id vào DB
    df["verdict"] = df["verdict"].fillna("UNKNOWN")   # bài chưa chấm xong -> gán nhãn rõ ràng

    return df


if __name__ == "__main__":
    raw = fetch_submissions(HANDLE, count=50)
    df = transform(raw)

    print(df.head(10))
    print("\nSố dòng, số cột:", df.shape)
    print("\nKiểu dữ liệu từng cột:\n", df.dtypes)