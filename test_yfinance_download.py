import yfinance as yf
from datetime import datetime, timedelta

def test_download():
    ticker = "AAPL"
    print(f"Testing yf.download for {ticker}")
    
    # Try different approaches
    
    # 1. Standard download for last few days
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"Downloading from {start_date} to {end_date}...")
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        print("Data shape:", data.shape)
        print(data)
        if data.empty:
            print("Download returned empty.")
        else:
            print("Download successful.")
            print(data.tail(1))
    except Exception as e:
        print("Download failed:", e)

    print("-" * 20)
    
    # 2. Ticker history with start/end
    print(f"Testing Ticker.history with start/end for {ticker}")
    try:
        dat = yf.Ticker(ticker)
        hist = dat.history(start=start_date, end=end_date)
        print("History shape:", hist.shape)
        print(hist)
    except Exception as e:
        print("History failed:", e)

if __name__ == "__main__":
    test_download()
