S&P 500 Stock Data Pipeline

A mini Data Engineering project created to practice building an end-to-end data pipeline using Python, PostgreSQL, and Docker Compose.

The pipeline fetches daily stock data for 30 major S&P 500 companies from the Alpha Vantage API, handles rate limits, and stores the data cleanly in PostgreSQL without duplicates.

📌 Features

API Integration: Fetches daily stock quotes (GLOBAL_QUOTE) from Alpha Vantage.

Rate Limit Handling: Pauses between requests to respect free-tier API limits.

Idempotent Storage: Uses PostgreSQL UPSERT (ON CONFLICT DO UPDATE) to avoid inserting duplicate records for the same stock on the same day.

Containerization: Runs the entire stack (PostgreSQL + Python Pipeline) using Docker Compose with a single command.

SQL Analytics: Includes basic SQL scripts to analyze stock prices, volatility, and trading volume.

🛠️ Tech Stack

Language: Python 3.10

Database: PostgreSQL 15

Libraries: requests, psycopg2-binary, python-dotenv

DevOps: Docker & Docker Compose

📁 Project Structure

dataenproject/
├── main_pipeline.py     # Main ETL script (API -> PostgreSQL)
├── analytics.sql        # Basic SQL queries for data analysis
├── Dockerfile           # Docker configuration for Python app
├── docker-compose.yml   # Multi-container setup (DB + Pipeline)
├── requirements.txt     # Python dependencies
├── .env.example         # Template for environment variables
└── README.md            # Project documentation


🚀 How to Run

1. Prerequisites

Docker & Docker Desktop installed.

Alpha Vantage API Key (Get a free key here).

2. Setup Environment Variables

Clone the repository and create a .env file from .env.example:

git clone https://github.com/dxkillmy/sp500-stock-etl-pipeline.git
cd sp500-stock-etl-pipeline
cp .env.example .env


Open .env and put your actual API_KEY.

3. Start the Pipeline

Run the following command to start PostgreSQL and execute the ETL pipeline automatically:

docker compose up --build


Note: Because of Alpha Vantage free tier limits (5 requests/min), processing all 30 stocks will take around 5-6 minutes.

4. Run SQL Analytics

To inspect the ingested stock data, run the analysis script inside the running PostgreSQL container:

docker exec -i stock_postgres psql -U root -d stock_db < analytics.sql


Created as part of my Data Engineering learning journey.