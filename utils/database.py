import csv
import os
import psycopg2
from psycopg2.extras import execute_values


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "stock_db"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        connect_timeout=10,
    )

def setup_database(conn):
    with conn, conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS raw;
            CREATE SCHEMA IF NOT EXISTS analytics;

            CREATE TABLE IF NOT EXISTS raw.stock_prices (
                ticker VARCHAR(10), trade_date DATE,
                open NUMERIC(12, 4), high NUMERIC(12, 4), low NUMERIC(12, 4),
                close NUMERIC(12, 4), volume BIGINT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ticker, trade_date)
            );

            CREATE TABLE IF NOT EXISTS analytics.dim_stock (
                ticker VARCHAR(10) PRIMARY KEY,
                company_name TEXT, sector TEXT, sub_industry TEXT
            );

            CREATE TABLE IF NOT EXISTS analytics.fact_stock_prices (
                ticker VARCHAR(10) REFERENCES analytics.dim_stock (ticker),
                trade_date DATE,
                open NUMERIC(12, 4), high NUMERIC(12, 4), low NUMERIC(12, 4),
                close NUMERIC(12, 4), volume BIGINT,
                daily_change_pct NUMERIC(10, 2),
                PRIMARY KEY (ticker, trade_date)
            );
        """)


def load_dim_stock(conn, path="data/stocks.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        rows = [(r["ticker"], r["company_name"], r["sector"], r["sub_industry"])
                for r in csv.DictReader(f)]
    with conn, conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO analytics.dim_stock (ticker, company_name, sector, sub_industry)
            VALUES %s
            ON CONFLICT (ticker) DO UPDATE SET
                company_name = EXCLUDED.company_name, sector = EXCLUDED.sector,
                sub_industry = EXCLUDED.sub_industry;
        """, rows)
    return [r[0] for r in rows]


def save_raw_prices(conn, symbol, df):
    rows = [(symbol, day, float(o), float(h), float(lo), float(c), int(v))
            for day, o, h, lo, c, v in zip(df.index, df.Open, df.High, df.Low, df.Close, df.Volume)]
    with conn, conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO raw.stock_prices (ticker, trade_date, open, high, low, close, volume)
            VALUES %s
            ON CONFLICT (ticker, trade_date) DO UPDATE SET
                open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low,
                close = EXCLUDED.close, volume = EXCLUDED.volume,
                updated_at = CURRENT_TIMESTAMP;
        """, rows)


def transform_to_analytics(conn):
    with conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO analytics.fact_stock_prices
                (ticker, trade_date, open, high, low, close, volume, daily_change_pct)
            SELECT ticker, trade_date, open, high, low, close, volume,
                   ROUND((close - LAG(close) OVER w) / NULLIF(LAG(close) OVER w, 0) * 100, 2)
            FROM raw.stock_prices
            WINDOW w AS (PARTITION BY ticker ORDER BY trade_date)
            ON CONFLICT (ticker, trade_date) DO UPDATE SET
                open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low,
                close = EXCLUDED.close, volume = EXCLUDED.volume,
                daily_change_pct = EXCLUDED.daily_change_pct;
        """)