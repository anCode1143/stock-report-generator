import yfinance as yf
import pandas_ta as ta
import pandas as pd
import os
import glob

class StockDataHandler:
    """
    Handles fetching, processing, and cleaning of stock data.
    """
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.csv_dir = os.path.join(project_root, "data")
        self.file_path = os.path.join(self.csv_dir, f"{self.ticker}.csv")
        os.makedirs(self.csv_dir, exist_ok=True)

    def fetch_and_prepare_data(self, period="6mo", interval="4h"):
        stock = yf.download(self.ticker, period=period, interval=interval, auto_adjust=False)

        if stock is None or stock.empty:
            print(f"❌ No data found for {self.ticker} with period={period}, interval={interval}")
            return None

        # Flatten MultiIndex columns by taking only the first level (removes ticker suffix)
        if isinstance(stock.columns, pd.MultiIndex):
            stock.columns = stock.columns.get_level_values(0)
        
        stock.ta.rsi(close=stock["Close"], length=14, append=True)
        stock.ta.macd(close=stock["Close"], append=True)
        stock.ta.sma(close=stock["Close"], length=20, append=True)
        stock.ta.sma(close=stock["Close"], length=50, append=True)

        stock.to_csv(self.file_path)
        print(f"Saved {self.ticker}.csv with {len(stock)} rows.")
        return self.file_path

    def clean_csv(self, warmup_period=50):
        try:
            df = pd.read_csv(self.file_path)
            
            if len(df) <= warmup_period:
                print(f"ERROR {os.path.basename(self.file_path)}: Only {len(df)} rows (need >{warmup_period})")
                return False
            
            original_rows = len(df)
            df_cleaned = df.iloc[warmup_period:].reset_index(drop=True)
            df_cleaned.to_csv(self.file_path, index=False)
            
            print(f"{os.path.basename(self.file_path)}: {original_rows} → {len(df_cleaned)} rows (cleaned)")
            return True
            
        except Exception as e:
            print(f"❌ Error cleaning {os.path.basename(self.file_path)}: {e}")
            return False

if __name__ == "__main__":
    print("=== Stock Data Generator ===")
    ticker = input("Enter stock ticker symbol (e.g., AAPL, TSLA): ").strip()
    
    if not ticker:
        print("❌ No ticker provided. Exiting.")
    else:
        handler = StockDataHandler(ticker)
        
        print(f"\nFetching data for {ticker}...")
        csv_path = handler.fetch_and_prepare_data(period="6mo", interval="4h")
        
        if csv_path:
            print(f"\n🧹 Cleaning data...")
            success = handler.clean_csv(warmup_period=50)
            
            if success:
                print(f"\nSuccessfully generated and cleaned {ticker}.csv")
            else:
                print(f"\nData fetched but cleaning failed.")
        else:
            print(f"\n❌ Failed to fetch data for {ticker}")