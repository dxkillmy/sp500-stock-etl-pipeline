def validate_prices(df):
    prices = df[["Open", "High", "Low", "Close"]]

    ok = prices.notna().all(axis=1) & df["Volume"].notna()  # ไม่มีค่าว่าง
    ok &= (prices > 0).all(axis=1)                          # ราคาต้องเป็นบวก
    ok &= df["High"] >= df["Low"]                           # high ต้องไม่ต่ำกว่า low
    ok &= df["Volume"] >= 0                                 # volume ต้องไม่ติดลบ

    return df[ok], int((~ok).sum())