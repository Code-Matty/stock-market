
from data_fetcher import DataFetcher
import sys

# Try with a definitely invalid ticker
invalid_ticker = "INVALID_TICKER_NAME_123"
print(f"Attempting to fetch data for: {invalid_ticker}")
try:
    data = DataFetcher.fetch_stock_data(invalid_ticker)
    if data:
        print("Data fetched successfully (unexpected for invalid ticker)")
    else:
        print("Data fetch returned None (expected)")
except Exception as e:
    print(f"Caught unexpected exception outside fetch_stock_data: {e}")

print("-" * 20)

# Try with a valid ticker to ensure it works normally
valid_ticker = "AAPL"
print(f"Attempting to fetch data for: {valid_ticker}")
data = DataFetcher.fetch_stock_data(valid_ticker)
if data:
    print("Data fetched successfully")
else:
    print("Failed to fetch data for valid ticker")
