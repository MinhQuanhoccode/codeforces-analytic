# Codeforces Analytics — ETL Pipeline

Pipeline dữ liệu tự động: Trích xuất lịch sử nộp bài từ Codeforces API → Làm sạch và chuẩn hóa schema bằng pandas → Nạp và đồng bộ vào PostgreSQL (Supabase) bằng SQLAlchemy.

**Mục tiêu**: Dự án thực hành kỹ thuật Data Engineering nền tảng — xử lý dữ liệu bán cấu trúc (nested JSON), thiết kế đường ống dữ liệu có tính lũy kế/chạy lại an toàn (Idempotent Pipeline), tối ưu hóa kiểu dữ liệu bộ nhớ và thao tác cơ sở dữ liệu quan hệ qua SQL Engine.

**Tech Stack**: Python 3.12, pandas, SQLAlchemy, PostgreSQL (Supabase), Requests.

---

## 1. Cấu trúc thư mục

```text
codeforces-analytic/
├── .env                  # Chứa credentials bí mật (bị .gitignore chặn hoàn toàn)
├── .env.example          # File mẫu cấu hình môi trường chuẩn
├── .gitignore             # Cấu hình loại trừ cache, bytecode và secrets
├── README.md              # Tài liệu kiến trúc và hướng dẫn vận hành
└── Project/
    ├── config.py          # Điểm tập trung biến cấu hình (HANDLE, DATABASE_URL)
    ├── extract.py          # Tầng trích xuất dữ liệu từ Codeforces REST API
    ├── transform.py        # Tầng biến đổi, flatten JSON và chuẩn hóa schema
    ├── load.py             # Tầng nạp dữ liệu, thực thi UPSERT vào database
    ├── main.py             # Orchestrator điều phối toàn bộ vòng đời pipeline
    └── requirements.txt    # Danh sách thư viện phụ thuộc
```

---

## 2. Database Schema (DDL)

Chạy câu lệnh DDL sau trong SQL Editor trên Supabase trước khi kích hoạt pipeline:

```sql
CREATE TABLE IF NOT EXISTS submissions (
    id BIGINT PRIMARY KEY,
    submitter_handle TEXT NOT NULL,
    problem_name TEXT,
    problem_rating INT,
    verdict TEXT,
    "programmingLanguage" TEXT,
    submit_time TIMESTAMP,
    "timeConsumedMillis" INT,
    "memoryConsumedBytes" BIGINT
);
```

> **Lưu ý**: Cột `id` bắt buộc phải là `PRIMARY KEY` (hoặc có ràng buộc `UNIQUE`) để hỗ trợ cơ chế đồng bộ `ON CONFLICT (id)`.

---

## 3. Cài đặt & Vận hành

### Bước 1: Khởi tạo môi trường ảo

```bash
# Di chuyển vào thư mục dự án
cd Project

# Tạo môi trường ảo ở thư mục cha
python -m venv ../.venv

# Kích hoạt môi trường ảo
# Windows:
..\.venv\Scripts\activate
# macOS / Linux:
source ../.venv/bin/activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### Bước 2: Thiết lập biến môi trường

Sao chép file cấu hình mẫu ra thư mục gốc:

```bash
# Windows:
copy ..\.env.example ..\.env

# macOS/Linux:
cp ../.env.example ../.env
```

Mở file `../.env` và cập nhật thông tin kết nối Supabase thật:

```env
DATABASE_URL=postgresql://postgres.<PROJECT_ID>:<PASSWORD>@<HOST>:5432/postgres
CF_HANDLE=Minwannacry
```

`CF_HANDLE` là handle Codeforces muốn crawl — nếu không khai báo, `config.py` sẽ tự dùng giá trị mặc định `"Minwannacry"`.

### Bước 3: Kích hoạt Pipeline

```bash
python main.py
```

---

## 4. Quyết định kiến trúc (Architecture Decisions)

* **Phân tách trách nhiệm (Separation of Concerns):** Phân chia rõ rệt 3 tầng **Extract → Transform → Load** độc lập. Mỗi module chỉ thực thi một chức năng duy nhất, không tự động chạy code khi được `import`. File `main.py` đóng vai trò nhạc trưởng (Orchestrator) duy nhất điều phối luồng chạy.
* **Cấu hình tập trung (Centralized Configuration):** Tất cả các tham số toàn cục (`HANDLE`, chuỗi kết nối DB) được đọc qua biến môi trường tại `config.py`, có giá trị mặc định dự phòng nếu `.env` chưa khai báo — tránh việc rải rác biến môi trường qua nhiều file.
* **Tôn trọng Rate Limit:** Codeforces áp dụng rate limit ~1 request/giây. Pipeline cấu hình gọi tập trung và thiết lập `timeout` nghiêm ngặt cho mỗi request.
* **Cơ chế Idempotent UPSERT:** Thay vì dùng `INSERT` thuần túy hoặc `DO NOTHING`, hệ thống sử dụng cú pháp `ON CONFLICT (id) DO UPDATE` để vừa tránh duplicate bản ghi, vừa tự động làm mới trạng thái chấm bài (`verdict`) khi chạy lại nhiều lần.

---

## 5. Xử lý & Chuẩn hóa dữ liệu (Transformation)

Payload trả về từ API Codeforces chứa các cấu trúc JSON lồng nhau (nested schema) cần làm phẳng (flatten) trước khi ánh xạ vào bảng quan hệ:

1. **`problem` (dict):** Chứa metadata bài toán. Trích xuất `name` thành `problem_name` và `rating` thành `problem_rating`. Dùng phương thức `.get()` để tránh `KeyError` đối với các bài tập chưa có rating.
2. **`author.members` (list chứa dict):** Cấu trúc lồng sâu 2 cấp. Trích xuất định danh người nộp bằng lambda expression: `a["members"][0]["handle"]`.
3. **`creationTimeSeconds` (Unix Timestamp):** Chuyển đổi sang đối tượng `pd.Timestamp` bằng `pd.to_datetime(..., unit="s")` để tương thích với cột `TIMESTAMP` trong PostgreSQL.

---

## 6. An toàn bảo mật (Security & Secret Rotation)

* **Quản lý Secrets:** File `.env` chứa chuỗi kết nối cơ sở dữ liệu đã được cấu hình loại trừ tuyệt đối trong `.gitignore`. File mẫu `.env.example` được cung cấp để chuẩn hóa việc triển khai.
* **Ứng phó sự cố (Secret Rotation):** Trong quá trình phát triển, khi phát hiện credential từng bị phân tán ra ngoài môi trường cô lập, quy trình **Secret Rotation** được thực hiện ngay lập tức: vô hiệu hóa mật khẩu cũ trên Supabase Cloud Dashboard, cấp phát mật khẩu mới và cô lập hoàn toàn chuỗi kết nối vào runtime environment.

---

## 7. Bài học thực tế & Tối ưu hóa (Lessons Learned)

### 7.1. Lỗi Type Coercion (`NaN` → `NULL`) và Tối ưu hóa Vectorization

* **Vấn đề:** Khi trích xuất các bài tập contest chưa gán độ khó hoặc bài gym, giá trị `rating` bị thiếu. pandas tự động gán `NaN` vào cột `problem_rating`, khiến kiểu dữ liệu của cột bị ép sang `float64`. Khi thực thi insert bằng SQLAlchemy vào cột PostgreSQL kiểu `INT`/`BIGINT`, chuỗi giá trị `NaN` bị coi là không hợp lệ và gây lỗi `NumericValueOutOfRange`.
* **Tiến hóa giải pháp:**
  * *Cách tiếp cận ban đầu:* Duyệt vòng lặp lồng nhau qua danh sách `records` bằng Python thuần và hàm `math.isnan()` để thay thế thành `None`. Cách này tốn tài nguyên tính toán khi số lượng bản ghi lớn, vì phải lặp qua từng phần tử bằng Python thay vì tận dụng xử lý hàng loạt (vectorized) của pandas:

```python
    # Cách cũ: Duyệt thủ công từng phần tử
    for r in records:
        for key, value in r.items():
            if isinstance(value, float) and math.isnan(value):
                r[key] = None
```

  * *Tối ưu hóa hiện tại (Vectorization):* Xử lý trực tiếp trên toàn bộ DataFrame bằng cơ chế vector hóa của pandas, trước khi chuyển đổi sang định dạng `dict` để insert:

```python
    # Cách tối ưu: Vectorized replacement trên toàn bộ bảng
    df = df.astype(object).where(pd.notnull(df), None)
    records = df.to_dict(orient="records")
```

* **Bài học:** Dữ liệu thực tế từ API luôn có thể thiếu field ở 1 số bản ghi — test với ít dữ liệu (`count=5`) dễ bỏ sót các trường hợp edge case này. Nên test lại với `count` lớn hơn trước khi coi pipeline là ổn định.


### 7.2. Giải quyết rủi ro Dữ liệu cũ (Stale Data) bằng UPSERT

* **Vấn đề:** Nếu sử dụng `ON CONFLICT (id) DO NOTHING`, một submission được crawl lúc đang chấm (`verdict = "TESTING"`) sẽ không bao giờ được cập nhật kết quả chính thức (`verdict = "OK"`) ở các lần chạy sau do `id` đã tồn tại trong DB.
* **Xử lý:** Chuyển sang cơ chế `DO UPDATE SET` có chọn lọc, chỉ cập nhật các trường có khả năng biến đổi (`verdict`, `timeConsumedMillis`, `memoryConsumedBytes`, `problem_rating`), giữ nguyên các trường cố định (`submit_time`, `submitter_handle`).

### 7.3. Chống treo tiến trình (Network Hanging Mitigation)

* Ban đầu, hàm gọi API thiếu tham số ngắt kết nối. Nếu server Codeforces bị nghẽn hoặc ngắt socket đột ngột, tiến trình sẽ bị kẹt vĩnh viễn (hanging state).
* **Xử lý:** Bổ sung `timeout=10` vào mọi network request kèm kiểm tra mã phản hồi HTTP (`response.raise_for_status()`).

### 7.4. Loại bỏ Code dư thừa (Dead Code Elimination)

* Cột `problem_tags` được flatten nhưng không nằm trong danh sách các cột cần nạp vào DB (`keep_cols`), gây lãng phí chu kỳ xử lý. Cột này đã được loại bỏ hoàn toàn khỏi transform step.

---

## 8. Hạn chế hiện tại & Kế hoạch mở rộng (Roadmap)

* [ ] **Chuẩn hóa Naming Convention:** Đồng bộ 100% tên cột sang chuẩn `snake_case` (ví dụ: đổi `"programmingLanguage"` thành `programming_language`).
* [ ] **Automated Testing:** Bổ sung bộ kiểm thử tự động (Unit Test với `pytest`) cho logic flatten của hàm `transform()`.
* [ ] **Batch Processing:** Chia nhỏ payload thành các batch nhỏ hơn khi số lượng submission tăng lên hàng ngàn bản ghi để kiểm soát lượng RAM tiêu thụ.
* [ ] **Orchestration nâng cao:** Tích hợp công cụ lập lịch định kỳ (cron job hoặc Apache Airflow / Prefect) để pipeline tự động thu thập dữ liệu hàng ngày.