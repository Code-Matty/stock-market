import pymongo
from pymongo import MongoClient
import config

class DBManager:
    def __init__(self):
        self.client = MongoClient(config.MONGO_URI)
        self.db = self.client[config.DB_NAME]
        self._init_collections()

    def _init_collections(self):
        """Initialize collections if they don't exist."""
        # Collections are created lazily in MongoDB, but we can ensure indexes or initial data here if needed.
        # Check if Configuration exists, if not create default
        if config.COLLECTION_CONFIGURATION not in self.db.list_collection_names():
            self.set_configuration(config.DEFAULT_LOOP_INTERVAL_SECONDS)

    def get_my_stocks(self):
        """Retrieve all stocks from MyStocks collection."""
        return list(self.db[config.COLLECTION_MY_STOCKS].find())

    def add_stock(self, full_name, short_name, isin, market_country, currency, market_type):
        """Add a new stock to monitor."""
        stock = {
            "FullName": full_name,
            "ShortName": short_name,
            "ISIN": isin,
            "MarketCountry": market_country,
            "Currency": currency,
            "MarketType": market_type
        }
        return self.db[config.COLLECTION_MY_STOCKS].insert_one(stock)

    def save_stock_data(self, stock_data):
        """Save fetched stock data to StockData collection."""
        return self.db[config.COLLECTION_STOCK_DATA].insert_one(stock_data)

    def find_stock_ticker(self, identifier):
        """Find stock ticker by FullName, ShortName, or ISIN (case-insensitive)."""
        query = {
            "$or": [
                {"FullName": {"$regex": identifier, "$options": "i"}},
                {"ShortName": {"$regex": identifier, "$options": "i"}},
                {"ISIN": {"$regex": identifier, "$options": "i"}}
            ]
        }
        stock = self.db[config.COLLECTION_MY_STOCKS].find_one(query)
        if stock:
            return stock.get('ShortName')
        return None

    def get_configuration(self):
        """Get the loop interval configuration."""
        config_doc = self.db[config.COLLECTION_CONFIGURATION].find_one()
        if config_doc and "loop_interval_seconds" in config_doc:
            return config_doc["loop_interval_seconds"]
        return config.DEFAULT_LOOP_INTERVAL_SECONDS

    def set_configuration(self, seconds):
        """Set the loop interval configuration."""
        # Upsert configuration (mono-record)
        self.db[config.COLLECTION_CONFIGURATION].replace_one(
            {}, 
            {"loop_interval_seconds": seconds}, 
            upsert=True
        )

    def close(self):
        self.client.close()

if __name__ == "__main__":
    # Test connection and initialization
    try:
        db_manager = DBManager()
        print(f"Connected to MongoDB at {config.MONGO_URI}")
        print(f"Database: {config.DB_NAME}")
        
        # Add a sample stock if MyStocks is empty
        stocks = db_manager.get_my_stocks()
        if not stocks:
            print("Adding sample stock AAPL...")
            db_manager.add_stock(
                "Apple Inc.", "AAPL", "US0378331005", "USA", "USD", "Technology"
            )
        
        print(f"Current stocks: {len(db_manager.get_my_stocks())}")
        print(f"Loop interval: {db_manager.get_configuration()} seconds")
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
