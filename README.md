# S&P 500 Data Pipeline & Analytics Warehouse

An automated, fault-tolerant ETL pipeline that ingests daily stock market data, applies data quality gates, and transforms raw prices into an analytics-ready Star Schema using PostgreSQL and Apache Airflow.

---

## Architecture & Data Flow

[ yfinance API ]
│
▼
[ Data Quality Gate ] ── (Filter nulls, negative prices, invalid High/Low)
│
▼
[ PostgreSQL: raw.stock_prices ] ── (Raw layer, Upsert via ON CONFLICT)
│
▼
[ SQL Transformations ] ── (In-DB Window Functions: % Change, SMA-20)
│
▼
[ PostgreSQL: analytics.fact_stock_prices ] ── (Presentation layer)
│
▼
[ Discord Webhook / Airflow DAG ] ── (Alerting & Orchestration)

---

## 🛠️ Key Technical Features

* **Medallion Architecture**: Separates immutable raw ingestion (`raw.stock_prices`) from presentation analytics (`analytics.fact_stock_prices`).
* **Idempotent Ingestion**: Handles rerun safety and backfills using PostgreSQL `ON CONFLICT (ticker, trade_date) DO UPDATE` (Upsert logic).
* **Data Quality Checks**: Intercepts corrupt data before database writes (filters out negative bounds, `High < Low` anomalies, and missing values).
* **Fault Isolation**: Exception handling inside ingestion loops guarantees individual symbol failures do not crash the pipeline.
* **In-Database Analytics**: Computes financial indicators (Daily Change %, 20-Day Simple Moving Average) directly inside PostgreSQL using SQL Window Functions (`LAG`, `OVER`).
* **Orchestration & Observability**: Scheduled via Apache Airflow with real-time Discord notifications reporting ingestion summary and rejected rows.

---

## Data Model (Star Schema)

### `analytics.dim_stock`
| Column | Type | Description |
| :--- | :--- | :--- |
| `ticker` | VARCHAR(10) | Primary Key (e.g., AAPL, NVDA) |
| `company_name` | TEXT | Company name |
| `sector` | TEXT | GICS Sector |
| `sub_industry` | TEXT | GICS Sub-Industry |

### `analytics.fact_stock_prices`
| Column | Type | Description |
| :--- | :--- | :--- |
| `ticker` | VARCHAR(10) | Foreign Key -> `dim_stock.ticker` |
| `trade_date` | DATE | Composite Primary Key |
| `open` / `high` / `low` / `close` | NUMERIC(12,4) | Daily stock prices |
| `volume` | BIGINT | Trading volume |
| `daily_change_pct` | NUMERIC(10,2) | Daily price movement (%) calculated via SQL |

---

## Quick Start

### 1. Prerequisites
* Docker & Docker Compose
* Git

### 2. Setup Environment
Clone the repository and set up environment variables:
```bash
git clone https://github.com/dxkillmy/sp500-stock-etl-pipeline.git
cd sp500-stock-etl-pipeline
cp .env.example .env
```

### 3. Run Pipeline via Docker Compose
Start PostgreSQL, Airflow, and database migrations:
```bash
docker compose up -d
```

### 4. Run Pipeline Manually (Optional)
To trigger the ETL script outside of Airflow:
```bash
docker exec -it stock_postgres python main_pipeline.py

Sample Analytics Query
20-Day Moving Average (SMA 20) for Apple (AAPL):
```SQL
SELECT 
    trade_date, 
    close,
    ROUND(AVG(close) OVER (
        ORDER BY trade_date 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ), 2) AS sma_20
FROM analytics.fact_stock_prices
WHERE ticker = 'AAPL'
ORDER BY trade_date DESC
LIMIT 10;