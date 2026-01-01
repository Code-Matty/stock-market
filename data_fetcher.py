import yfinance as yf
from datetime import datetime, timedelta
import config

class DataFetcher:
    @staticmethod
    def fetch_stock_data(ticker_symbol):
        """
        Fetches the latest data for a given ticker symbol using yfinance.
        
        Args:
            ticker_symbol (str): The stock ticker (e.g., "AAPL").
            
        Returns:
            dict: A dictionary containing the fetched data, or None if failed.
        """
        try:
            # Use yf.download which is often more robust and common in tutorials
            # Fetch for the last 5 days to ensure we get a trading day
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)
            
            # threads=False to avoid multitasking issues in some envs
            hist = yf.download(ticker_symbol, start=start_date, end=end_date, progress=False, threads=False)
            
            if hist.empty:
                print(f"No data found for {ticker_symbol}")
                if config.ENABLE_MOCK_DATA:
                    print(f"Generating MOCK data for {ticker_symbol}")
                    import random
                    base_price = 150.0 # Arbitrary base
                    open_p = base_price + random.uniform(-5, 5)
                    close_p = open_p + random.uniform(-2, 2)
                    return {
                        "Ticker": ticker_symbol,
                        "Date": datetime.now(),
                        "Open": round(open_p, 2),
                        "High": round(max(open_p, close_p) + 1, 2),
                        "Low": round(min(open_p, close_p) - 1, 2),
                        "Close": round(close_p, 2),
                        "Volume": random.randint(1000, 100000)
                    }
                return None
            
            # Get the latest row
            latest_data = hist.iloc[-1]
            
            # Handle MultiIndex columns if present (yfinance changed this recently)
            # recent yfinance download returns columns like (Price, Ticker) -> we need to access properly
            # But with single ticker it might be flat. Let's check keys or access by string.
            
            # Safe access helper
            def get_val(row, key):
                try:
                    # Try accessing directly
                    val = row[key]
                    # If it's a Series (multi-index), take first/only item 
                    if hasattr(val, 'item'):
                        return float(val.item())
                    return float(val)
                except:
                    # Fallback for weird shapes
                    return 0.0

            current_time = datetime.now()
            
            data_dict = {
                "Ticker": ticker_symbol,
                "Date": current_time,
                "Open": get_val(latest_data, "Open"),
                "High": get_val(latest_data, "High"),
                "Low": get_val(latest_data, "Low"),
                "Close": get_val(latest_data, "Close"),
                "Volume": int(get_val(latest_data, "Volume")),
            }
            
            return data_dict
            
        except Exception as e:
            error_msg = str(e)
            if "No timezone found" in error_msg:
                 print(f"Error fetching data for {ticker_symbol}: yfinance library error (No timezone found). Try upgrading yfinance: 'pip install --upgrade yfinance'")
            else:
                 print(f"Error fetching data for {ticker_symbol}: {e}")
            if config.ENABLE_MOCK_DATA:
                print(f"Generating MOCK data for {ticker_symbol} due to error")
                import random
                base_price = 150.0 
                open_p = base_price + random.uniform(-5, 5)
                close_p = open_p + random.uniform(-2, 2)
                return {
                    "Ticker": ticker_symbol,
                    "Date": datetime.now(),
                    "Open": round(open_p, 2),
                    "High": round(max(open_p, close_p) + 1, 2),
                    "Low": round(min(open_p, close_p) - 1, 2),
                    "Close": round(close_p, 2),
                    "Volume": random.randint(1000, 100000)
                }
            return None

    @staticmethod
    def fetch_stock_info(ticker_symbol):
        """
        Fetches metadata for a given ticker symbol.
        Returns a dict with FullName, ShortName, ISIN, MarketCountry, Currency, MarketType.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Accessing .info triggers the fetch
            info = ticker.info
            
            # Try getting ISIN from property (most reliable) or info dict
            isin = getattr(ticker, 'isin', None)
            if not isin or isin == '-':
                isin = info.get('isin', 'N/A')
            
            return {
                "FullName": info.get('longName', 'N/A'),
                "ShortName": info.get('symbol', ticker_symbol),
                "ISIN": isin,
                "MarketCountry": info.get('country', 'N/A'),
                "Currency": info.get('currency', 'N/A'),
                "MarketType": info.get('sector', 'N/A')
            }
        except Exception as e:
            print(f"Error fetching info for {ticker_symbol}: {e}")
            return None

    @staticmethod
    def fetch_historical_data(ticker_symbol, period="1y"):
        """
        Fetches historical data for a given ticker symbol.
        Args:
            ticker_symbol (str): The stock ticker.
            period (str): The period to fetch (default "1y").
        Returns:
            pandas.DataFrame: The historical data, or empty DataFrame if failed.
        """
        try:
            # threading=False is safer for some environments
            hist = yf.download(ticker_symbol, period=period, progress=False, threads=False)
            if hist.empty:
                print(f"No historical data found for {ticker_symbol}")
                return None
            return hist
        except Exception as e:
            print(f"Error fetching historical data for {ticker_symbol}: {e}")
            return None

if __name__ == "__main__":
    # Test
    print("Fetching data for AAPL...")
    data = DataFetcher.fetch_stock_data("AAPL")
    print(data)
