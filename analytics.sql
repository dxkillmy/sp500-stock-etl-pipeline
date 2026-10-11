-- ============================================================
-- Data Mart / Analytical Views for Stock Market Analysis
-- ============================================================

-- 1. ดูราคาหุ้น พร้อมคำนวณส่วนต่างราคา (High-Low) และมูลค่าการซื้อขายรวม
SELECT 
    symbol,
    latest_trading_day,
    open,
    price AS close_price,
    high,
    low,
    (high - low) AS price_range,
    (price * volume) AS total_trading_value
FROM daily_stocks;


-- 2. หุ้นที่ราคาแพงที่สุด 5 อันดับแรก
SELECT 
    symbol, 
    price, 
    volume, 
    latest_trading_day
FROM daily_stocks
ORDER BY price DESC
LIMIT 5;


-- 3. หุ้นที่มีปริมาณการซื้อขาย (Volume) สูงสุด 5 อันดับแรก
SELECT 
    symbol, 
    price, 
    volume, 
    latest_trading_day
FROM daily_stocks
ORDER BY volume DESC
LIMIT 5;


-- 4. หุ้นที่มีราคาผันผวนระหว่างวันเกิน $5
SELECT 
    symbol, 
    price, 
    (high - low) AS price_range,
    latest_trading_day
FROM daily_stocks
WHERE (high - low) > 5.0
ORDER BY price_range DESC;