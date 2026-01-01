
import time
from datetime import datetime
import threading
import cmd
from db_manager import DBManager
from data_fetcher import DataFetcher
from stock_analyzer import StockAnalyzer

def analyze_stock(stock_data):
    """
    Simple analysis of stock data.
    """
    if not stock_data:
        return
    
    ticker = stock_data['Ticker']
    open_price = stock_data['Open']
    close_price = stock_data['Close']
    
    change = close_price - open_price
    percent_change = (change / open_price) * 100 if open_price else 0
    
    trend = "NEUTRAL"
    if change > 0:
        trend = "POSITIVE"
    elif change < 0:
        trend = "NEGATIVE"
        
    print(f"Analysis for {ticker}: Open={open_price:.2f}, Close={close_price:.2f}, Change={percent_change:.2f}% -> Trend: {trend}")

import argparse
import sys

def run_loop(stop_event=None):
    print("Starting Stock Market App Loop...")
    db_manager = DBManager()
    
    while True:
        if stop_event and stop_event.is_set():
            print("Stopping loop via signal...")
            break

        try:
            # 1. Read configuration for loop interval
            interval = db_manager.get_configuration()
            print(f"\n--- Starting cycle (Interval: {interval}s) ---")
            
            # 2. Get list of stocks to monitor
            my_stocks = db_manager.get_my_stocks()
            if not my_stocks:
                print("No stocks in MyStocks. Please add stocks to the database.")
            
            for stock in my_stocks:
                if stop_event and stop_event.is_set(): break
                
                ticker = stock.get('ShortName') # Assuming ShortName is the ticker (e.g. AAPL)
                
                if not ticker:
                    print(f"Skipping stock with no ShortName: {stock}")
                    continue
                
                print(f"Processing {ticker}...")
                
                # 3. Read delta/fetch data
                data = DataFetcher.fetch_stock_data(ticker)
                
                if data:
                    # 4. Save data to StockData
                    db_manager.save_stock_data(data)
                    print(f"Saved data for {ticker}")
                    
                    # 5. Evaluate/Analyze
                    # analyze_stock(data) # OLD simple analysis
                    
                    # 6. Deep Analysis (Bull/Bear)
                    # Fetch history for this specific stock
                    print(f"  > Performing Deep Analysis for {ticker}...")
                    hist_data = DataFetcher.fetch_historical_data(ticker, period="1y")
                    if hist_data is not None and not hist_data.empty:
                        analyzer = StockAnalyzer(hist_data)
                        report = analyzer.evaluate()
                        print_analysis_report(ticker, report)
                    else:
                        print(f"  > Could not fetch history for deep analysis of {ticker}")
            
            if stop_event and stop_event.is_set(): break
            
            print(f"--- Cycle complete. Sleeping for {interval} seconds ---")
            # Sleep in chunks to allow faster stopping
            for _ in range(int(interval)):
                if stop_event and stop_event.is_set(): break
                time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nStopping application...")
            break
        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
            # Sleep a bit to avoid rapid error loops
            time.sleep(5)

    db_manager.close()

def find_stock(identifier):
    db_manager = DBManager()
    print(f"Searching for stock with identifier: '{identifier}'...")
    
    # Try to resolve identifier from DB
    ticker = db_manager.find_stock_ticker(identifier)
    
    if ticker:
        print(f"Found in MyStocks: {ticker}")
    else:
        print(f"'{identifier}' not found in MyStocks. Assuming it is a Ticker symbol.")
        ticker = identifier
        
    print(f"Fetching data for: {ticker}")
    data = DataFetcher.fetch_stock_data(ticker)
    
    if data:
        print("\n--- Stock Information ---")
        for key, value in data.items():
            print(f"{key}: {value}")
        print("-------------------------")
    else:
        print(f"Could not fetch data for {ticker}")
        
    db_manager.close()

def save_stock(identifier):
    print(f"Fetching metadata for '{identifier}'...")
    info = DataFetcher.fetch_stock_info(identifier)
    
    if info:
        db_manager = DBManager()
        # FullName, ShortName, ISIN, MarketCountry, Currency, MarketType
        result = db_manager.add_stock(
            info['FullName'],
            info['ShortName'],
            info['ISIN'],
            info['MarketCountry'],
            info['Currency'],
            info['MarketType']
        )
        print(f"Successfully added stock: {info['FullName']} ({info['ShortName']})")
        print(f"Details: ISIN={info['ISIN']}, Country={info['MarketCountry']}, Currency={info['Currency']}, Type={info['MarketType']}")
        db_manager.close()
    else:
        print(f"Could not fetch metadata for '{identifier}'. Please check the ticker symbol.")

def print_analysis_report(ticker, report):
    print("\n" + "="*40)
    print(f"REPORT: {ticker}")
    print("="*40)
    print(f"MARKET STATUS: {report['Status']}")
    print("-" * 40)
    
    if report['Status'] == "INSUFFICIENT_DATA":
        for signal in report.get("Signals", []):
            print(f"  > {signal}")
        print("="*40 + "\n")
        return

    t = report['Trend']
    print(f"TREND (SMA):")
    print(f"  Price: {t['Price']} | SMA50: {t['SMA50']} | SMA200: {t['SMA200']}")
    print(f"  Signal: {t['Cross']}")
    
    m = report['Momentum']
    print(f"MOMENTUM:")
    print(f"  RSI: {m['RSI']} ({m['RSI_Status']})")
    print(f"  MACD: {m['MACD_Signal']}")
    
    q = report['Quantitative']
    print(f"PERFORMANCE (12m):")
    print(f"  Return: {q['Return_12m_Percent']}%")
    print(f"  Max Drawdown: {q['Max_Drawdown_Percent']}%")
    print("="*40 + "\n")

def analyze_stock_detailed(identifier):
    print(f"Fetching 1 year historical data for '{identifier}'...")
    # 1. Resolve identifier to ticker if needed (reuse find logic or just assume ticker)
    # For simplicity, similar to find-stock, let's try to resolve first
    db_manager = DBManager()
    ticker = db_manager.find_stock_ticker(identifier) or identifier
    db_manager.close()
    
    data = DataFetcher.fetch_historical_data(ticker, period="1y")
    
    if data is not None and not data.empty:
        print(f"Analyzing {ticker}...")
        analyzer = StockAnalyzer(data)
        report = analyzer.evaluate()
        print_analysis_report(ticker, report)
    else:
        print(f"Could not fetch historical data for {ticker}.")

class StockShell(cmd.Cmd):
    intro = 'Welcome to the Stock Market App Shell. Type help or ? to list commands.\n'
    prompt = '(stock-app) '
    
    def __init__(self):
        super().__init__()
        self.monitor_thread = None
        self.stop_event = threading.Event()

    def do_monitor(self, arg):
        'Control background monitoring: monitor start | monitor stop'
        if arg == 'start':
            if self.monitor_thread and self.monitor_thread.is_alive():
                print("Monitoring is already running.")
            else:
                self.stop_event.clear()
                self.monitor_thread = threading.Thread(target=run_loop, args=(self.stop_event,), daemon=True)
                self.monitor_thread.start()
                print("Monitoring loop started in background.")
        elif arg == 'stop':
            if self.monitor_thread and self.monitor_thread.is_alive():
                print("Stopping monitoring loop... (may take up to 1 second)")
                self.stop_event.set()
                self.monitor_thread.join(timeout=5)
                print("Monitoring stopped.")
            else:
                print("Monitoring is not running.")
        else:
            print("Usage: monitor <start|stop>")

    def do_find(self, arg):
        'Find stock info: find <identifier>'
        if not arg:
            print("Usage: find <identifier>")
            return
        find_stock(arg)

    def do_save(self, arg):
        'Save new stock: save <ticker>'
        if not arg:
            print("Usage: save <ticker>")
            return
        save_stock(arg)

    def do_analyze(self, arg):
        'Analyze stock (Bull/Bear): analyze <identifier>'
        if not arg:
            print("Usage: analyze <identifier>")
            return
        analyze_stock_detailed(arg)

    def do_exit(self, arg):
        'Exit the shell'
        print("Exiting...")
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_event.set()
            self.monitor_thread.join(timeout=2)
        return True

    def do_quit(self, arg):
        'Exit the shell'
        return self.do_exit(arg)

def main():
    parser = argparse.ArgumentParser(description="Stock Market App")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # 'run' command
    subparsers.add_parser("run", help="Run the continuous monitoring loop (CLI mode)")
    
    # 'find-stock' command
    find_parser = subparsers.add_parser("find-stock", help="Find and display stock info")
    find_parser.add_argument("identifier", help="Stock Name, Short Name, or ISIN")

    # 'save-stock' command
    save_parser = subparsers.add_parser("save-stock", help="Add a new stock to MyStocks")
    save_parser.add_argument("identifier", help="Ticker Symbol (e.g. AAPL, RACE.MI)")

    # 'analyze-stock' command
    analyze_parser = subparsers.add_parser("analyze-stock", help="Perform deep technical analysis (Bull/Bear)")
    analyze_parser.add_argument("identifier", help="Stock Name, Short Name, or ISIN")

    # 'interactive' command
    subparsers.add_parser("interactive", help="Start interactive shell mode")

    # 'help' command
    subparsers.add_parser("help", help="Show this help message and exit")
    
    if len(sys.argv) == 1:
        # Default behavior: Interactive Mode
        StockShell().cmdloop()
    else:
        args = parser.parse_args()
        if args.command == "run":
            run_loop()
        elif args.command == "find-stock":
            find_stock(args.identifier)
        elif args.command == "save-stock":
            save_stock(args.identifier)
        elif args.command == "analyze-stock":
            analyze_stock_detailed(args.identifier)
        elif args.command == "interactive":
            StockShell().cmdloop()
        elif args.command == "help":
            parser.print_help()

if __name__ == "__main__":
    main()
