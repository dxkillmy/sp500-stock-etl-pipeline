import os
import time
import yfinance as yf
from dotenv import load_dotenv

load_dotenv() 

from utils.alert import send_discord_alert
from utils.quality import validate_prices
from utils.database import (
    get_db_connection, setup_database, load_dim_stock, save_raw_prices, transform_to_analytics,
)

# 5d = โหมดรายวัน (ดึงย้อนหลัง 5 วัน รันซ้ำได้เพราะเป็น upsert)
# ครั้งแรกให้ตั้ง PERIOD=1y เพื่อดึงข้อมูลย้อนหลังทั้งปี
PERIOD = os.getenv("PERIOD", "5d")


def fetch_prices(symbol):
    try:
        df = yf.Ticker(symbol).history(period=PERIOD, auto_adjust=False)
    except Exception as e:
        raise RuntimeError(f"download failed ({type(e).__name__})") from None
    if df.empty:
        raise RuntimeError("no data returned")
    df.index = df.index.date
    return df


def run_pipeline():
    send_discord_alert(f" Starting Stock Data Pipeline (period={PERIOD})")
    conn = get_db_connection()
    setup_database(conn)
    symbols = load_dim_stock(conn)

    success, failed, bad_rows = 0, [], 0
    for symbol in symbols:
        try:
            df = fetch_prices(symbol)
            df, rejected = validate_prices(df)
            bad_rows += rejected
            if df.empty:
                raise ValueError("all rows rejected by quality checks")
            save_raw_prices(conn, symbol, df)
            print(f"✅ Ingested {symbol} ({len(df)} rows)")
            success += 1
        except Exception as e:  # หุ้นตัวเดียวพัง ต้องไม่ทำให้ตัวอื่นหยุดตาม
            print(f"⚠️ {symbol} failed: {e}")
            failed.append(symbol)
        time.sleep(1)

    transform_to_analytics(conn)
    conn.close()

    send_discord_alert(
        f" Pipeline Completed!\n Successful: `{success}`\n Failed: `{failed}`\n"
        f" Rows rejected by quality checks: `{bad_rows}`"
    )
    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    run_pipeline()