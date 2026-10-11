import os
import time
import psycopg2
import requests
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "stock_db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "1234")

# รายชื่อหุ้นตัวอย่างที่ต้องการติดตาม
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX"]

def get_db_connection():
    """เชื่อมต่อกับ PostgreSQL Database"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def create_table():
    """สร้างตาราง daily_stocks ใน PostgreSQL หากยังไม่มี"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS daily_stocks (
        symbol VARCHAR(10),
        latest_trading_day DATE,
        open NUMERIC(10, 4),
        high NUMERIC(10, 4),
        low NUMERIC(10, 4),
        price NUMERIC(10, 4),
        volume BIGINT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (symbol, latest_trading_day)
    );
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Created table 'daily_stocks' successfully.")

def fetch_and_save_stock_data(symbol):
    """ดึงข้อมูลหุ้นจาก Alpha Vantage API แล้ว บันทึกลง PostgreSQL"""
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()

        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            trading_day = quote.get("07. latest trading day")
            open_p = float(quote.get("02. open", 0))
            high_p = float(quote.get("03. high", 0))
            low_p = float(quote.get("04. low", 0))
            price = float(quote.get("05. price", 0))
            volume = int(quote.get("06. volume", 0))

            insert_query = """
            INSERT INTO daily_stocks (symbol, latest_trading_day, open, high, low, price, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, latest_trading_day) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                price = EXCLUDED.price,
                volume = EXCLUDED.volume,
                updated_at = CURRENT_TIMESTAMP;
            """
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(insert_query, (symbol, trading_day, open_p, high_p, low_p, price, volume))
            conn.commit()
            cur.close()
            conn.close()
            print(f"📈 Inserted data for {symbol} ({trading_day}) successfully.")
        else:
            print(f"⚠️ Rate limit reached or symbol not found for {symbol}.")
    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")

def run_pipeline():
    print("🚀 Starting Data Pipeline...")
    create_table()
    
    for symbol in STOCKS:
        fetch_and_save_stock_data(symbol)
        time.sleep(2)  # ชะลอคำสั่งป้องกัน API Limit
        
    print("🎉 Pipeline executed successfully!")

if __name__ == "__main__":
    run_pipeline()