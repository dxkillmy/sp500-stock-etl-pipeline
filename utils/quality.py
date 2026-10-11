def validate_data(symbol, quote):
    """Data Quality Check: ตรวจสอบความถูกต้องของข้อมูลก่อนลง Database"""
    trading_day = quote.get("07. latest trading day")
    price = float(quote.get("05. price", 0))
    open_p = float(quote.get("02. open", 0))
    high = float(quote.get("03. high", 0))
    low = float(quote.get("04. low", 0))

    if not trading_day:
        return False, "Missing trading day"
    if price <= 0 or open_p <= 0:
        return False, f"Invalid price range (Price: {price}, Open: {open_p})"
    if high < low:
        return False, f"High price ({high}) is lower than Low price ({low})"

    return True, "Valid"