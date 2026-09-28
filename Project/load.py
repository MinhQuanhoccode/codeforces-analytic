import pandas as pd
from sqlalchemy import create_engine, text
from config import DATABASE_URL


def load_to_db(df: pd.DataFrame, table_name: str = "submissions"):
    """Insert DataFrame vào bảng trên Supabase, tự động cập nhật bản ghi nếu đã tồn tại id."""
    if df.empty:
        print("DataFrame rỗng, không có dữ liệu để insert.")
        return

    if not DATABASE_URL:
        raise ValueError("Không tìm thấy DATABASE_URL trong file .env!")

    print("🔌 Đang kết nối tới Supabase...")
    engine = create_engine(DATABASE_URL)

    # Vectorized: chuyển toàn bộ NaN thành None tương thích với SQL NULL
    df = df.astype(object).where(pd.notnull(df), None)
    records = df.to_dict(orient="records")

    insert_sql = text(f"""
        INSERT INTO {table_name}
        (id, submitter_handle, problem_name, problem_rating, verdict,
         "programmingLanguage", submit_time, "timeConsumedMillis", "memoryConsumedBytes")
        VALUES
        (:id, :submitter_handle, :problem_name, :problem_rating, :verdict,
         :programmingLanguage, :submit_time, :timeConsumedMillis, :memoryConsumedBytes)
        ON CONFLICT (id) DO UPDATE SET
            verdict = EXCLUDED.verdict,
            problem_rating = EXCLUDED.problem_rating,
            "timeConsumedMillis" = EXCLUDED."timeConsumedMillis",
            "memoryConsumedBytes" = EXCLUDED."memoryConsumedBytes";
    """)

    with engine.begin() as conn:
        conn.execute(insert_sql, records)

    print(f"✅ Đã xử lý {len(records)} dòng (UPSERT thành công) vào bảng '{table_name}'.")