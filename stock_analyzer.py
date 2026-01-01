
import pandas as pd
import numpy as np

class StockAnalyzer:
    def __init__(self, data):
        """
        Initialize with historical data.
        Args:
            data (pandas.DataFrame): Historical stock data (must contain 'Close' column).
        """
        self.data = data
        self._ensure_data_validity()

    def _ensure_data_validity(self):
        # Handle yfinance multi-index columns if present (e.g. ('Close', 'AAPL'))
        if isinstance(self.data.columns, pd.MultiIndex):
            # Attempt to flatten or select the first level if it's 'Close'
            # For data fetched via yf.download(period='1y'), it might have Ticker levels
            # We'll just try accessing 'Close' directly or cleaning up column names
            try:
                # If columns are like (Price, Ticker), accessing 'Close' might return a DF with tickers as cols
                # or a Series if single ticker.
                pass 
            except Exception:
               pass
        
        # Ensure 'Close' is available and numeric
        # We work with standard yf.download structure. 
        # Case 1: Columns = ['Open', 'High', 'Low', 'Close', ...] (Simple)
        # Case 2: Columns = MultiIndex (['Close'], ['AAPL']) (Complex)
        
        # We will dynamically find the Close column
        pass

    def _get_series(self, column_name='Close'):
        """Helper to safely get a data series respecting yfinance changing formats."""
        if column_name in self.data:
            col = self.data[column_name]
            # If it's a DataFrame (multi-ticker structure but we expect one), take first col
            if isinstance(col, pd.DataFrame):
                return col.iloc[:, 0]
            return col
        # Fallback for some multi-index shapes
        try:
             # Try XS or similar if needed, but let's assume yf.download with single ticker
             # usually gives a structure we can access.
             # If data has MultiIndex columns, data['Close'] usually works.
             return self.data['Close']
        except KeyError:
             raise ValueError(f"Column {column_name} not found in data")

    def calculate_sma(self, period):
        series = self._get_series('Close')
        return series.rolling(window=period).mean()

    def calculate_rsi(self, period=14):
        series = self._get_series('Close')
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, fast=12, slow=26, signal=9):
        series = self._get_series('Close')
        exp1 = series.ewm(span=fast, adjust=False).mean()
        exp2 = series.ewm(span=slow, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def calculate_bollinger_bands(self, period=20, std_dev=2):
        series = self._get_series('Close')
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band

    def calculate_metrics(self):
        series = self._get_series('Close')
        if len(series) < 2:
            return {}
            
        current_price = float(series.iloc[-1])
        # Approx 12 months ago (252 trading days)
        limit = min(252, len(series)-1)
        price_12m_ago = float(series.iloc[-limit])
        
        total_return = ((current_price - price_12m_ago) / price_12m_ago) * 100
        
        # Max Drawdown
        # Roll max
        rolling_max = series.cummax()
        drawdown = (series - rolling_max) / rolling_max
        max_drawdown = float(drawdown.min()) * 100
        
        return {
            "TotalReturn12m": total_return,
            "MaxDrawdown": max_drawdown,
            "CurrentPrice": current_price
        }

    def evaluate(self):
        """
        Performs the 4-phase analysis and returns a comprehensive report.
        """
        report = {"Status": "UNKNOWN", "Signals": [], "Metrics": {}}
        
        series = self._get_series('Close')
        if len(series) < 200:
            report["Status"] = "INSUFFICIENT_DATA"
            report["Signals"].append("Not enough data to calculate SMA200 (Need >200 days)")
            return report

        # 1. Trend Indicators
        sma50 = self.calculate_sma(50)
        sma200 = self.calculate_sma(200)
        
        current_sma50 = sma50.iloc[-1]
        current_sma200 = sma200.iloc[-1]
        current_price = series.iloc[-1]
        
        # Bull/Bear by SMA200
        is_bullish_trend = current_price > current_sma200
        trend_status = "BULLISH" if is_bullish_trend else "BEARISH"
        
        # Golden/Death Cross (simplified check of current state)
        # Ideally we check recent crossover, but current state gives primary trend
        cross_signal = "Golden Cross (50 > 200)" if current_sma50 > current_sma200 else "Death Cross (50 < 200)"

        # 2. Momentum
        rsi = self.calculate_rsi(14)
        current_rsi = rsi.iloc[-1]
        
        macd_line, signal_line, _ = self.calculate_macd()
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        
        momentum_status = "NEUTRAL"
        if current_rsi > 70:
             momentum_status = "OVERBOUGHT (Risk of correction)"
        elif current_rsi < 30:
             momentum_status = "OVERSOLD (Potential bounce)"
             
        macd_status = "Bullish" if current_macd > current_signal else "Bearish"

        # 3. Volatility
        upper, lower = self.calculate_bollinger_bands()
        # Bandwidth could indicate volatility squeezing
        
        # 4. Quantitative
        metrics = self.calculate_metrics()
        
        # Final Decision
        # We weigh the SMA200 heavily for the primary label
        main_label = "MERCATO TORO (Bull Market)" if is_bullish_trend else "MERCATO ORSO (Bear Market)"
        if is_bullish_trend and current_sma50 < current_sma200:
             main_label += " - Weakening (Correction?)"
        elif not is_bullish_trend and current_sma50 > current_sma200:
             main_label += " - Recovering (Potential Reversal?)"

        report["Status"] = main_label
        report["Trend"] = {
            "Price": round(current_price, 2),
            "SMA200": round(current_sma200, 2),
            "SMA50": round(current_sma50, 2),
            "Cross": cross_signal
        }
        report["Momentum"] = {
            "RSI": round(current_rsi, 2),
            "RSI_Status": momentum_status,
            "MACD_Signal": macd_status
        }
        report["Quantitative"] = {
            "Return_12m_Percent": round(metrics.get("TotalReturn12m", 0.0), 2),
            "Max_Drawdown_Percent": round(metrics.get("MaxDrawdown", 0.0), 2)
        }
        
        return report
