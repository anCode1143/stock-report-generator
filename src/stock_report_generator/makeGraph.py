import os

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd


class GraphGenerator:
    """
    Generates and saves technical analysis graphs for a given stock ticker.
    """

    def __init__(self, ticker):
        self.ticker = ticker.upper()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.csv_path = os.path.join(project_root, "data", f"{self.ticker}.csv")
        self.graphs_dir = os.path.join(project_root, "graphs")
        os.makedirs(self.graphs_dir, exist_ok=True)

        self.df = self._load_and_prepare_data()

    def _load_and_prepare_data(self):
        df = pd.read_csv(self.csv_path)

        date_col = None
        for col in df.columns:
            if col.lower() in ["datetime", "date"]:
                date_col = col
                break

        if date_col is not None:
            df[date_col] = pd.to_datetime(df[date_col])
            df.columns = df.columns.str.strip()
            df.set_index(date_col, inplace=True)
            return df
        else:
            raise ValueError("No datetime or date column found in CSV")

    def plot_ma_and_volume(self):
        add_plots = [
            mpf.make_addplot(self.df["SMA_20"], color="blue", width=1),
            mpf.make_addplot(self.df["SMA_50"], color="navy", width=1),
        ]

        fig, axes = mpf.plot(
            self.df,
            type="candle",
            style="yahoo",
            addplot=add_plots,
            volume=True,
            ylabel="Price",
            ylabel_lower="Volume",
            figratio=(20, 6),
            figscale=1.5,
            panel_ratios=(5, 1),
            returnfig=True,
        )

        lines = axes[0].get_lines()
        axes[0].legend(handles=lines[-2:], labels=["SMA 20", "SMA 50"], loc="upper left")
        fig.suptitle("Trend and MAs", fontsize=16, y=0.92)

        vol_ax = axes[2]
        vol_ax.spines["top"].set_linewidth(1.5)
        vol_ax.spines["top"].set_color("black")

        save_path = os.path.join(self.graphs_dir, "MAs.png")
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"✅ Saved MAs chart to {save_path}")

    def plot_macd(self):
        macd_line = mpf.make_addplot(self.df["MACD_12_26_9"], color="red", width=1.6)
        signal_line = mpf.make_addplot(self.df["MACDs_12_26_9"], color="orange", width=1.6)
        macd_hist = mpf.make_addplot(self.df["MACDh_12_26_9"], type="bar", color="navy", alpha=0.6)

        fig, _ = mpf.plot(
            self.df,
            type="line",
            style="yahoo",
            linecolor="black",
            addplot=[macd_hist, macd_line, signal_line],
            figratio=(12, 4),
            figscale=1.2,
            returnfig=True,
        )
        fig.suptitle("MACD", fontsize=14, y=0.92)

        save_path = os.path.join(self.graphs_dir, "macd.png")
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"✅ Saved MACD chart to {save_path}")

    def plot_rsi(self):
        rsi_df = self.df[["RSI_14"]].copy()
        rsi_df["RSI_30"] = 30
        rsi_df["RSI_70"] = 70
        rsi_df["Open"] = float("nan")
        rsi_df["High"] = float("nan")
        rsi_df["Low"] = float("nan")
        rsi_df["Close"] = float("nan")

        rsi_line = mpf.make_addplot(rsi_df["RSI_14"], color="purple", width=1.4)
        rsi_30 = mpf.make_addplot(rsi_df["RSI_30"], color="black", width=2)
        rsi_70 = mpf.make_addplot(rsi_df["RSI_70"], color="black", width=2)

        fig, axes = mpf.plot(
            rsi_df,
            type="line",
            linecolor="none",
            style="yahoo",
            addplot=[rsi_line, rsi_30, rsi_70],
            ylabel="RSI (14)",
            figratio=(12, 3),
            figscale=1.2,
            returnfig=True,
        )

        axes[0].set_ylim(0, 100)
        axes[0].set_yticks(range(0, 101, 10))
        axes[0].axhspan(70, 100, facecolor="red", alpha=0.08)
        axes[0].axhspan(0, 30, facecolor="green", alpha=0.08)
        axes[0].twinx().set_visible(False)
        axes[0].spines["right"].set_visible(False)
        fig.suptitle("RSI (14)", fontsize=14, y=0.95)

        save_path = os.path.join(self.graphs_dir, "rsi.png")
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"✅ Saved RSI chart to {save_path}")

    def generate_all(self):
        self.plot_ma_and_volume()
        self.plot_macd()
        self.plot_rsi()


if __name__ == "__main__":
    try:
        # Example usage:
        ticker = "NVDA"
        print(f"[*] Generating graphs for {ticker}...")
        generator = GraphGenerator(ticker)
        generator.generate_all()
        print("\n All graphs generated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
