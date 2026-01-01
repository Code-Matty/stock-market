import yfinance as yf
import requests

def test_fetch():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    })
    
    print("yfinance version:", yf.__version__)

    try:
        # Pass the session if possible. Older yfinance might not support it directly in Ticker? 
        # Actually newer yfinance doesn't take session in Ticker(session=...).
        # We might need to override the shared session.
        # But let's try just basic Ticker first, maybe the downgrade helped but I need headers.
        
        # yfinance 0.2.x uses requests_cache or internal session?
        # It seems yfinance automatically handles headers usually.
        
        # Let's try to simply fetch data.
        ticker_sym = "AAPL"
        print(f"Fetching {ticker_sym}...")
        
        dat = yf.Ticker(ticker_sym)
        hist = dat.history(period="1d")
        print(hist)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch()
