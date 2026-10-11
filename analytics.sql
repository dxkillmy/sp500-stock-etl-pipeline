-- 1. สรุปภาพรวมหุ้นทั้งหมดจาก Analytics Layer
SELECT 
    symbol,
    latest_trading_day,
    price,
    daily_change_pct,
    price_range,
    trading_value
FROM analytics.daily_stock_summary
ORDER BY trading_value DESC;

-- 2. หุ้นที่ราคาเปลี่ยนมากที่สุด (%)
SELECT 
    symbol,
    price,
    daily_change_pct
FROM analytics.daily_stock_summary
ORDER BY ABS(daily_change_pct) DESC
LIMIT 3;