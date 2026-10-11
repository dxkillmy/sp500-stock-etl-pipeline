import os
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "stock_db"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", "1234")
    )

def setup_database(conn):
    """สร้าง Raw และ Analytics Schemas"""
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        cur.execute("CREATE SCHEMA IF NOT EXISTS analytics;")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.daily_stocks (
                symbol VARCHAR(10),
                latest_trading_day DATE,
                open NUMERIC(10, 4), high NUMERIC(10, 4), low NUMERIC(10, 4),
                price NUMERIC(10, 4), volume BIGINT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, latest_trading_day)
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS analytics.daily_stock_summary (
                symbol VARCHAR(10), latest_trading_day DATE,
                price NUMERIC(10, 4), daily_change_pct NUMERIC(10, 2),
                price_range NUMERIC(10, 4), trading_value NUMERIC(15, 2),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, latest_trading_day)
            );
        """)
        conn.commit()

def save_raw_stock(conn, symbol, quote):
    """Insert ข้อมูลลง raw schema"""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO raw.daily_stocks (symbol, latest_trading_day, open, high, low, price, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, latest_trading_day) DO UPDATE SET
                open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, 
                price = EXCLUDED.price, volume = EXCLUDED.volume, updated_at = CURRENT_TIMESTAMP;
        """, (
            symbol, quote["07. latest trading day"], quote["02. open"], 
            quote["03. high"], quote["04. low"], quote["05. price"], quote["06. volume"]
        ))
        conn.commit()

def transform_to_analytics(conn):
    """Transform ข้อมูลไปยัง analytics schema"""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO analytics.daily_stock_summary (
                symbol, latest_trading_day, price, daily_change_pct, price_range, trading_value
            )
            SELECT 
                symbol, latest_trading_day, price,
                ROUND(((price - open) / NULLIF(open, 0)) * 100, 2) AS daily_change_pct,
                (high - low) AS price_range, (price * volume) AS trading_value
            FROM raw.daily_stocks
            ON CONFLICT (symbol, latest_trading_day) DO UPDATE SET
                price = EXCLUDED.price, daily_change_pct = EXCLUDED.daily_change_pct,
                price_range = EXCLUDED.price_range, trading_value = EXCLUDED.trading_value,
                updated_at = CURRENT_TIMESTAMP;
        """)
        conn.commit()