
import yfinance as yf

print("Testing yf.Ticker(...).history(...)")
try:
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="5d")
    if not hist.empty:
        print("Success with Ticker.history!")
        print(hist.tail(1))
    else:
        print("Ticker.history returned empty.")
except Exception as e:
    print(f"Ticker.history failed: {e}")

print("-" * 20)
print("Testing yf.download(...) again for comparison")
try:
    data = yf.download("AAPL", period="5d", progress=False)
    if not data.empty:
        print("Success with download!")
    else:
        print("download returned empty.")
except Exception as e:
    print(f"download failed: {e}")
