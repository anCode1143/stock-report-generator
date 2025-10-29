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
        project_root = os.path.dirname(os.path.dirname(__file__))
        self.csv_dir = os.path.join(project_root, "CSVs")
        self.file_path = os.path.join(self.csv_dir, f"{self.ticker}.csv")
        os.makedirs(self.csv_dir, exist_ok=True)

    def fetch_and_prepare_data(self, period="6mo", interval="4h"):
        stock = yf.download(self.ticker, period=period, interval=interval, auto_adjust=False)

        if stock is None or stock.empty:
            print(f"❌ No data found for {self.ticker} with period={period}, interval={interval}")
            return None

        # Flatten MultiIndex columns if they exist
        if isinstance(stock.columns, pd.MultiIndex):
            stock.columns = ['_'.join(col).strip() for col in stock.columns.values]

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
    csv_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CSVs")
    print(f"Target directory: {csv_directory}")
    
    response = input("Do you want to proceed with cleaning all CSVs? (yes/no): ").lower().strip()
    
    if response == 'yes':
        csv_files = glob.glob(os.path.join(csv_directory, "*.csv"))
        if not csv_files:
            print("No CSV files found to clean.")
    else:
        print("Operation cancelled.")