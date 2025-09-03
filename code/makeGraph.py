import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import os

def makeGraph(ticker):
    # Load and clean data
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CSVs", ticker + ".csv")
    df = pd.read_csv(csv_path)

    date_col = None
    for col in df.columns:
        if col.lower() in ["datetime", "date"]:
            date_col = col
            break

    if date_col is not None:
        df[date_col] = pd.to_datetime(df[date_col])
        df.columns = df.columns.str.strip()
        df.set_index(date_col, inplace=True)
    else:
        raise ValueError("No datetime or date column found in CSV")

    # Create moving average overlays
    add_plots = [
        mpf.make_addplot(df["SMA_20"], color='blue', width=1),
        mpf.make_addplot(df["SMA_50"], color='navy', width=1),
    ]

    # Create the figure and axes using `returnfig=True`
    fig, axes = mpf.plot(
        df,
        type='candle',
        style='yahoo',
        addplot=add_plots,
        volume=True,
        ylabel="Price",
        ylabel_lower="Volume",
        figratio=(20, 6),
        figscale=1.5,
        panel_ratios=(5, 1),
        returnfig=True  # This allows us to manually edit the title and grids after plotting
    )

    # Extract actual plotted lines from axes[0] and assign labels
    lines = axes[0].get_lines()
    axes[0].legend(
        handles=lines[-2:],  # last two lines are likely SMA_20 and SMA_50
        labels=["SMA 20", "SMA 50"],
        loc="upper left"
    )

    # Set a custom title, positioned slightly lower
    fig.suptitle("Trend and MAs", fontsize=16, y=0.92)

    # Darken and thicken the horizontal separator line between the panels
    # That line is typically the top border of the volume axis
    vol_ax = axes[2]  # mplfinance returns 3 axes when volume=True: price, volume, and shared x-axis
    vol_ax.spines['top'].set_linewidth(1.5)
    vol_ax.spines['top'].set_color('black')


    # MACD
    macd_line = mpf.make_addplot(df["MACD_12_26_9"], color='red', width=1.6)
    signal_line = mpf.make_addplot(df["MACDs_12_26_9"], color='orange', width=1.6)
    macd_hist = mpf.make_addplot(df["MACDh_12_26_9"], type='bar', color='navy', alpha=0.6)

    fig_macd, axes_macd = mpf.plot(
        df,
        type='line',
        style='yahoo',
        linecolor='black',
        addplot=[macd_hist, macd_line, signal_line],
        figratio=(12, 4),
        figscale=1.2,
        returnfig=True
    )

    fig_macd.suptitle("MACD", fontsize=14, y=0.92)

    # Create a new RSI-only dataframe
    rsi_df = df[["RSI_14"]].copy()
    rsi_df["RSI_30"] = 30
    rsi_df["RSI_70"] = 70
    rsi_df["Open"] = float('nan')
    rsi_df["High"] = float('nan')
    rsi_df["Low"] = float('nan')
    rsi_df["Close"] = float('nan')

    # RSI lines
    rsi_line = mpf.make_addplot(rsi_df["RSI_14"], color='purple', width=1.4)
    rsi_30 = mpf.make_addplot(rsi_df["RSI_30"], color='black', width=2)
    rsi_70 = mpf.make_addplot(rsi_df["RSI_70"], color='black', width=2)

    # Plot
    fig_rsi, axes_rsi = mpf.plot(
        rsi_df,
        type='line',
        linecolor='none',
        style='yahoo',
        addplot=[rsi_line, rsi_30, rsi_70],
        ylabel="RSI (14)",
        figratio=(12, 3),
        figscale=1.2,
        returnfig=True
    )

    # Limit Y-axis
    axes_rsi[0].set_ylim(0, 100)
    axes_rsi[0].set_yticks(range(0, 101, 10))


    # Add shaded overbought (70–100) and oversold (0–30) zones
    axes_rsi[0].axhspan(70, 100, facecolor='red', alpha=0.08)
    axes_rsi[0].axhspan(0, 30, facecolor='green', alpha=0.08)

    # Clean up right axis
    axes_rsi[0].twinx().set_visible(False)
    axes_rsi[0].spines['right'].set_visible(False)

    # Lower the title slightly
    fig_rsi.suptitle("RSI (14)", fontsize=14, y=0.95)

    # Save graphs to relative paths
    graphs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "graphs")
    os.makedirs(graphs_dir, exist_ok=True)
    
    fig_rsi.savefig(os.path.join(graphs_dir, "rsi.png"), dpi=300, bbox_inches='tight')
    fig_macd.savefig(os.path.join(graphs_dir, "macd.png"), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(graphs_dir, "MAs.png"), dpi=300, bbox_inches='tight')