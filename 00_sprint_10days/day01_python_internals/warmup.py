# Danh sách bài tập mẫu từ Codeforces API
problems = [
    {"name": "Watermelon", "rating": 800, "tags": ["implementation"]},
    {"name": "Too Easy", "rating": 1200, "tags": ["math"]},
    {"name": "Maximum Subarray Sum", "rating": 1900, "tags": ["dp", "greedy"]},
    {"name": "Hard DP Problem", "rating": 2100, "tags": ["dp", "graphs"]},
]

# 1. Thêm 1 bài tập mới vào danh sách (tương đương vector.push_back trong C++)
problems.append({"name": "Thi Dau ICPC", "rating": 1400, "tags": ["math", "strings"]})

# 2. Lọc ra các bài có rating < 1500 HOẶC chứa tag "math" (List Comprehension)
filtered_problems = [
    p["name"] for p in problems 
    if p["rating"] < 1500 or "math" in p["tags"]
]

print("Các bài tập thỏa điều kiện:", filtered_problems)
import sys

print("=== 1. SO SÁNH NGUYÊN TỬ (PRIMITIVES) ===")
# Trong C++: int 32-bit tốn đúng 4 bytes (hoặc long long 64-bit tốn 8 bytes)
val = 100
print(f"Giá trị {val} trong Python tốn: {sys.getsizeof(val)} bytes")


print("\n=== 2. SO SÁNH DYNAMIC ARRAY (std::vector vs list) ===")
# Trong C++: std::vector<int> rỗng tốn 24 bytes (3 pointers: _Myfirst, _Mylast, _Myend)
empty_list = []
print(f"Python list rỗng tốn: {sys.getsizeof(empty_list)} bytes")


print("\n=== 3. CƠ CHẾ OVER-ALLOCATION (CAPACITY GROWTH) ===")
# Quan sát cách Python list tăng dung lượng (capacity) khi append phần tử
numbers = []
last_size = sys.getsizeof(numbers)

for i in range(16):
    numbers.append(i)
    current_size = sys.getsizeof(numbers)
    # Chỉ in ra khi Python thực hiện reallocate bộ nhớ
    if current_size != last_size or i == 0:
        print(f"Len: {len(numbers):2d} | Memory: {current_size:3d} bytes | (Reallocated!)")
        last_size = current_size