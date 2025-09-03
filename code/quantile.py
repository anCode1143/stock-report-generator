import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import QuantileRegressor
import datetime as dt
import os

def makeQuantile(ticker, forecast_horizon=6, alpha=0.01, window=20):
    """
    Generate quantile regression confidence forecast for a given ticker.
    
    Parameters:
    ticker (str): Stock ticker symbol
    forecast_horizon (int): Number of periods to forecast ahead
    alpha (float): Regularization parameter (lower means higher learning complexity)
    window (int): Lookback parameter when regression is called
    """
    
    # Standardize ticker to uppercase for consistency
    ticker = ticker.upper()
    
    # === CONFIG ===
    project_root = os.path.dirname(os.path.dirname(__file__))
    CSV_PATH = os.path.join(project_root, "CSVs", f"{ticker}.csv")
    FORECAST_HORIZON = forecast_horizon
    FEATURES = ["High", "Close", "Volume", "Low", "RSI_14", "MACD_12_26_9", "SMA_50"]
    ALPHA = alpha
    WINDOW = window

    # Ensure graphs directory exists
    graphs_dir = os.path.join(project_root, "graphs")
    os.makedirs(graphs_dir, exist_ok=True)
    
    print(f"[DEBUG] Starting quantile regression for {ticker}...")

    # === LOAD DATA ===
    df = pd.read_csv(CSV_PATH)
    
    # Always use the first column as datetime (more reliable than name matching)
    datetime_col = df.columns[0]
    df[datetime_col] = pd.to_datetime(df[datetime_col])
    
    # Rename to 'Datetime' for consistency in the rest of the code
    df = df.rename(columns={datetime_col: 'Datetime'})
    
    df = df.dropna(subset=FEATURES + ["Close"]).copy()

    # Create targets: highest and lowest close prices over next N candles
    df["future_high_close"] = df["Close"].rolling(window=FORECAST_HORIZON, min_periods=1).max().shift(-FORECAST_HORIZON+1)
    df["future_low_close"] = df["Close"].rolling(window=FORECAST_HORIZON, min_periods=1).min().shift(-FORECAST_HORIZON+1)
    df.dropna(inplace=True)
    # Use entire CSV - no history lookback limitation
    df = df.reset_index(drop=True)

    # === BACKTEST FORECAST RANGE ===
    # Upper bands predict highest close, lower bands predict lowest close
    q05_preds, q15_preds, q25_preds, q50_preds, q75_preds, q85_preds, q95_preds = [], [], [], [], [], [], []
    y_true_high, y_true_low = [], []

    # Initialize models outside the loop
    model_q05, model_q15, model_q25, model_q50, model_q75, model_q85, model_q95 = None, None, None, None, None, None, None

    for i in range(WINDOW):
        train_df = df.iloc[:-(WINDOW - i)]
        test_row = df.iloc[[-(WINDOW - i)]]

        # Lower quantiles predict the lowest close in the period
        model_q05 = QuantileRegressor(quantile=0.05, alpha=ALPHA).fit(train_df[FEATURES], train_df["future_low_close"])  # 90% band lower
        model_q15 = QuantileRegressor(quantile=0.15, alpha=ALPHA).fit(train_df[FEATURES], train_df["future_low_close"])  # 70% band lower
        model_q25 = QuantileRegressor(quantile=0.25, alpha=ALPHA).fit(train_df[FEATURES], train_df["future_low_close"])  # 50% band lower
        
        # Upper quantiles predict the highest close in the period
        model_q75 = QuantileRegressor(quantile=0.75, alpha=ALPHA).fit(train_df[FEATURES], train_df["future_high_close"])  # 50% band upper
        model_q85 = QuantileRegressor(quantile=0.85, alpha=ALPHA).fit(train_df[FEATURES], train_df["future_high_close"])  # 70% band upper
        model_q95 = QuantileRegressor(quantile=0.95, alpha=ALPHA).fit(train_df[FEATURES], train_df["future_high_close"])  # 90% band upper
        
        # Median predicts the average of high and low
        future_mid = (train_df["future_high_close"] + train_df["future_low_close"]) / 2
        model_q50 = QuantileRegressor(quantile=0.50, alpha=ALPHA).fit(train_df[FEATURES], future_mid)  # median

        q05_preds.append(model_q05.predict(test_row[FEATURES])[0])
        q15_preds.append(model_q15.predict(test_row[FEATURES])[0])
        q25_preds.append(model_q25.predict(test_row[FEATURES])[0])
        q50_preds.append(model_q50.predict(test_row[FEATURES])[0])
        q75_preds.append(model_q75.predict(test_row[FEATURES])[0])
        q85_preds.append(model_q85.predict(test_row[FEATURES])[0])
        q95_preds.append(model_q95.predict(test_row[FEATURES])[0])
        
        y_true_high.append(test_row["future_high_close"].values[0])
        y_true_low.append(test_row["future_low_close"].values[0])

    # Final live forecast from most recent row - train on full dataset
    train_df_final = df.iloc[:-1]  # Use all data except the last row for training
    latest_features = df[FEATURES].iloc[[-1]]

    # Train final models on full dataset - separate models for high and low
    # Lower quantiles predict lowest close
    final_model_q05 = QuantileRegressor(quantile=0.05, alpha=ALPHA).fit(train_df_final[FEATURES], train_df_final["future_low_close"])
    final_model_q15 = QuantileRegressor(quantile=0.15, alpha=ALPHA).fit(train_df_final[FEATURES], train_df_final["future_low_close"])
    final_model_q25 = QuantileRegressor(quantile=0.25, alpha=ALPHA).fit(train_df_final[FEATURES], train_df_final["future_low_close"])

    # Upper quantiles predict highest close
    final_model_q75 = QuantileRegressor(quantile=0.75, alpha=ALPHA).fit(train_df_final[FEATURES], train_df_final["future_high_close"])
    final_model_q85 = QuantileRegressor(quantile=0.85, alpha=ALPHA).fit(train_df_final[FEATURES], train_df_final["future_high_close"])
    final_model_q95 = QuantileRegressor(quantile=0.95, alpha=ALPHA).fit(train_df_final[FEATURES], train_df_final["future_high_close"])

    # Median predicts the middle of the range
    future_mid_final = (train_df_final["future_high_close"] + train_df_final["future_low_close"]) / 2
    final_model_q50 = QuantileRegressor(quantile=0.50, alpha=ALPHA).fit(train_df_final[FEATURES], future_mid_final)

    final_q05 = final_model_q05.predict(latest_features)[0]
    final_q15 = final_model_q15.predict(latest_features)[0]
    final_q25 = final_model_q25.predict(latest_features)[0]
    final_q50 = final_model_q50.predict(latest_features)[0]
    final_q75 = final_model_q75.predict(latest_features)[0]
    final_q85 = final_model_q85.predict(latest_features)[0]
    final_q95 = final_model_q95.predict(latest_features)[0]

    # Recent Close price and datetime for context
    close_recent = df["Close"].iloc[-WINDOW:].reset_index(drop=True)
    datetime_recent = df["Datetime"].iloc[-WINDOW:].reset_index(drop=True)

    # === PLOT ===
    plt.figure(figsize=(14, 6))
    plt.plot(datetime_recent, close_recent, label="Close Price", color="black", linewidth=2)

    # Confidence bands - more visible with better opacity
    plt.fill_between(datetime_recent, q05_preds, q95_preds, color="lightblue", alpha=0.2, label="90% Confidence Band")
    plt.fill_between(datetime_recent, q15_preds, q85_preds, color="cornflowerblue", alpha=0.3, label="70% Confidence Band")
    plt.fill_between(datetime_recent, q25_preds, q75_preds, color="royalblue", alpha=0.4, label="50% Confidence Band")

    # Live forecast confidence bands - extend beyond the last datetime
    last_datetime = datetime_recent.iloc[-1]
    # Create forecast datetime range (next few time periods)
    forecast_datetime = [last_datetime + dt.timedelta(days=1), last_datetime + dt.timedelta(days=2)]
    plt.fill_between(forecast_datetime, final_q05, final_q95, color="lightblue", alpha=0.2)
    plt.fill_between(forecast_datetime, final_q15, final_q85, color="cornflowerblue", alpha=0.3)
    plt.fill_between(forecast_datetime, final_q25, final_q75, color="royalblue", alpha=0.4)

    # Labels and layout
    plt.title(f"Quantile Regression Confidence Forecast - {ticker}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.tight_layout()
    
    # Use relative path for saving
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "graphs", f"{ticker}_quantile_forecast.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()  # Close the plot to free memory
    
    print(f"✅ Quantile forecast saved for {ticker}")
    
    # Return the forecast values for potential further use
    return {
        'q05': final_q05,
        'q15': final_q15,
        'q25': final_q25,
        'q50': final_q50,
        'q75': final_q75,
        'q85': final_q85,
        'q95': final_q95,
        'forecast_datetime': forecast_datetime
    }

if __name__ == "__main__":
    # Test the function
    makeQuantile("asml")