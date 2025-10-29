import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import QuantileRegressor
import datetime as dt
import os

class QuantileForecaster:
    """
    Generates and plots a quantile regression forecast for a given stock ticker.
    """
    def __init__(self, ticker, forecast_horizon=6, alpha=0.01, window=20):
        self.ticker = ticker.upper()
        self.forecast_horizon = forecast_horizon
        self.alpha = alpha
        self.window = window
        
        self.project_root = os.path.dirname(os.path.dirname(__file__))
        self.csv_path = os.path.join(self.project_root, "CSVs", f"{self.ticker}.csv")
        self.output_path = os.path.join(self.project_root, "graphs", f"{self.ticker}_quantile_forecast.png")
        
        self.features = ["High", "Close", "Volume", "Low", "RSI_14", "MACD_12_26_9", "SMA_50"]
        self.quantiles = [0.05, 0.15, 0.25, 0.50, 0.75, 0.85, 0.95]
        self.models = {}
        self.df = None

    def _load_and_prepare_data(self):
        print(f"[DEBUG] Loading and preparing data for {self.ticker}...")
        df = pd.read_csv(self.csv_path)
        
        datetime_col = df.columns[0]
        df[datetime_col] = pd.to_datetime(df[datetime_col])
        df = df.rename(columns={datetime_col: 'Datetime'})
        
        df = df.dropna(subset=self.features + ["Close"]).copy()

        df["future_high_close"] = df["Close"].rolling(window=self.forecast_horizon, min_periods=1).max().shift(-self.forecast_horizon + 1)
        df["future_low_close"] = df["Close"].rolling(window=self.forecast_horizon, min_periods=1).min().shift(-self.forecast_horizon + 1)
        df["future_mid_close"] = (df["future_high_close"] + df["future_low_close"]) / 2
        
        df.dropna(inplace=True)
        self.df = df.reset_index(drop=True)

    def _train_models(self, train_df):
        print(f"[DEBUG] Training {len(self.quantiles)} models...")
        X_train = train_df[self.features]
        
        for q in self.quantiles:
            model = QuantileRegressor(quantile=q, alpha=self.alpha, solver='highs-ds')
            
            # Lower quantiles predict low, upper predict high, median predicts middle
            if q < 0.5:
                y_train = train_df["future_low_close"]
            elif q > 0.5:
                y_train = train_df["future_high_close"]
            else:
                y_train = train_df["future_mid_close"]
                
            self.models[q] = model.fit(X_train, y_train)

    def _predict(self, features_df):
        predictions = {}
        for q, model in self.models.items():
            predictions[q] = model.predict(features_df)
        return pd.DataFrame(predictions)

    def plot_results(self, backtest_preds, forecast_pred):
        print("[DEBUG] Plotting results...")
        test_df = self.df.iloc[-self.window:]
        
        plt.figure(figsize=(14, 6))
        
        plt.plot(test_df['Datetime'], test_df['Close'], label="Close Price", color="black", linewidth=2)

        plt.fill_between(test_df['Datetime'], backtest_preds[0.05], backtest_preds[0.95], color="lightblue", alpha=0.3, label="90% Confidence")
        plt.fill_between(test_df['Datetime'], backtest_preds[0.15], backtest_preds[0.85], color="cornflowerblue", alpha=0.4, label="70% Confidence")
        plt.fill_between(test_df['Datetime'], backtest_preds[0.25], backtest_preds[0.75], color="royalblue", alpha=0.5, label="50% Confidence")

        last_datetime = test_df['Datetime'].iloc[-1]
        forecast_dates = [last_datetime + dt.timedelta(days=i) for i in range(1, self.forecast_horizon + 1)]
        
        forecast_range = forecast_pred.iloc[0]
        plt.fill_between(forecast_dates, forecast_range[0.05], forecast_range[0.95], color="lightblue", alpha=0.3)
        plt.fill_between(forecast_dates, forecast_range[0.15], forecast_range[0.85], color="cornflowerblue", alpha=0.4)
        plt.fill_between(forecast_dates, forecast_range[0.25], forecast_range[0.75], color="royalblue", alpha=0.5)

        plt.title(f"Quantile Regression Forecast for {self.ticker}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend(loc="upper left")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(self.output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Quantile forecast saved to {self.output_path}")

    def run(self):
        self._load_and_prepare_data()
        
        if len(self.df) <= self.window:
            print(f"Error: Not enough data for {self.ticker} to perform backtest. Need > {self.window} rows, have {len(self.df)}.")
            return None

        train_df = self.df.iloc[:-self.window]
        test_features = self.df.iloc[-self.window:][self.features]
        self._train_models(train_df)
        
        backtest_preds = self._predict(test_features)
        self._train_models(self.df)
        
        latest_features = self.df.iloc[[-1]][self.features]
        forecast_pred = self._predict(latest_features)
        
        self.plot_results(backtest_preds, forecast_pred)
        return forecast_pred.iloc[0].to_dict()

def makeQuantile(ticker, forecast_horizon=6, alpha=0.01, window=20):
    try:
        forecaster = QuantileForecaster(ticker, forecast_horizon, alpha, window)
        return forecaster.run()
    except Exception as e:
        print(f"An error occurred during quantile forecasting for {ticker}: {e}")
        return None

if __name__ == "__main__":
    makeQuantile("tsla", window=20)