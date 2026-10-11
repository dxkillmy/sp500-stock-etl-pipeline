import os
import time
import requests
from dotenv import load_dotenv

from utils.alert import send_discord_alert
from utils.quality import validate_data
from utils.database import get_db_connection, setup_database, save_raw_stock, transform_to_analytics

load_dotenv()

API_KEY = os.getenv("API_KEY")
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

def run_pipeline():
    send_discord_alert("🚀 **Starting Stock Data Pipeline execution...**")
    
    try:
        conn = get_db_connection()
        setup_database(conn)
    except Exception as e:
        err_msg = f"❌ **Database Connection Failed:** {e}"
        print(err_msg)
        send_discord_alert(err_msg)
        return

    success_count, rejected_count = 0, 0

    for symbol in STOCKS:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
        res = requests.get(url).json()

        if "Global Quote" in res and res["Global Quote"]:
            quote = res["Global Quote"]
            is_valid, reason = validate_data(symbol, quote)

            if is_valid:
                save_raw_stock(conn, symbol, quote)
                print(f"✅ [Data Quality PASSED] Ingested {symbol}")
                success_count += 1
            else:
                print(f"⚠️ [Data Quality FAILED] Rejected {symbol}: {reason}")
                rejected_count += 1
        else:
            print(f"⚠️ Fetching failed or rate limited for {symbol}")
            rejected_count += 1

        time.sleep(2)

    transform_to_analytics(conn)
    conn.close()

    summary_msg = f"🎉 **Pipeline Completed!**\n- Successful: `{success_count}`\n- Rejected/Failed: `{rejected_count}`"
    print(summary_msg)
    send_discord_alert(summary_msg)

if __name__ == "__main__":
    run_pipeline()