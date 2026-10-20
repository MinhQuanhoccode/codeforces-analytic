import os
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")
HANDLE = "dinosuit_man" #TEN TAI KHOAN CODEFORCES
COUNT = 100 #SO LUONG DATA CAN LAY