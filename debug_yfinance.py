import yfinance as yf

print("yfinance version:", yf.__version__)

try:
    ticker = yf.Ticker("AAPL")
    print("Fetching history...")
    hist = ticker.history(period="1d")
    print("History:")
    print(hist)
    
    if hist.empty:
        print("Empty history.")
except Exception as e:
    print(f"Error: {e}")
