import yfinance as yf
import pandas_ta as ta
import pandas as pd
import os

def makeCSV(ticker, period="6mo", interval="4h"):
    # Download 1 year of 4h candles for KKR
    stock = yf.download(ticker, period=period, interval=interval, auto_adjust=False)

    # Flatten MultiIndex to single-level
    stock.columns = [col[0] for col in stock.columns]

    # Add indicators
    stock.ta.rsi(close=stock["Close"], length=14, append=True)
    stock.ta.macd(close=stock["Close"], append=True)
    stock.ta.sma(close=stock["Close"], length=20, append=True)
    stock.ta.sma(close=stock["Close"], length=50, append=True)

    # Save to CSV - use relative path from project root
    csv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CSVs")
    os.makedirs(csv_dir, exist_ok=True)
    stock.to_csv(os.path.join(csv_dir, ticker + ".csv"))
    print("✅ Saved "+ticker+".csv")

if __name__ == "__main__":
            makeCSV("NVDA", period="2y")