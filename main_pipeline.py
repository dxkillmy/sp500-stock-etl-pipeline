import os
import time
from dotenv import load_dotenv
import psycopg2
import requests

# โหลดค่าจากไฟล์ .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "stock_db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "1234")