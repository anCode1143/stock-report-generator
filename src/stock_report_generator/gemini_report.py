import base64
import os
from datetime import datetime

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

from .prompts import get_analysis_prompt


class GeminiStockReportGenerator:
    """
    A class to generate comprehensive stock reports using Gemini.
    Integrates CSV data and multiple graph visualizations to create detailed analysis.
    """

    def __init__(self, api_key=None):
        """
        Initialize the GeminiStockReportGenerator.

        Args:
            api_key (str, optional): Google AI API key. If not provided, will try to get from environment.
        """
        # Ensure dotenv is loaded from the correct location
        self._load_environment()

        if api_key:
            print(f"🔑 Using provided API key: {api_key[:10]}...{api_key[-5:]}")
            genai.configure(api_key=api_key)
            self.api_key = api_key
        else:
            # Try to get from environment variable
            api_key = os.getenv("GOOGLE_AI_API_KEY")
            if api_key:
                print(f"🔑 Loaded API key from environment: {api_key[:10]}...{api_key[-5:]}")
                # Strip any whitespace or hidden characters
                api_key = api_key.strip()
                genai.configure(api_key=api_key)
                self.api_key = api_key
            else:
                raise ValueError(
                    "No API key provided. Please set GOOGLE_AI_API_KEY environment variable or pass api_key parameter."
                )

        # Test the API key immediately
        try:
            # Try to list models to verify API key works
            models = list(genai.list_models())
            print(f"✅ API key verified - {len(models)} models available")
        except Exception as e:
            print(f"❌ API key verification failed: {e}")
            raise ValueError(f"Invalid API key: {e}")

        # Initialize model with fallbacks
        self._initialize_model()

        # Base paths - go up from src/stock_report_generator to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.csv_path = os.path.join(project_root, "data") + "/"
        self.graphs_path = os.path.join(project_root, "graphs") + "/"

    def _load_environment(self):
        """
        Load environment variables from .env file, trying multiple locations.
        """
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(
            os.path.dirname(script_dir)
        )  # Go up two levels to project root

        # Try multiple .env locations in order of preference
        dotenv_locations = [
            os.path.join(project_root, ".env"),  # Project root
            os.path.join(script_dir, ".env"),  # Same directory as script
            ".env",  # Current working directory
        ]

        env_loaded = False
        for dotenv_path in dotenv_locations:
            if os.path.exists(dotenv_path):
                print(f"📁 Loading .env from: {dotenv_path}")
                load_dotenv(
                    dotenv_path=dotenv_path, override=True
                )  # override=True ensures it reloads
                env_loaded = True
                break

        if not env_loaded:
            print("⚠️  No .env file found in expected locations:")
            for path in dotenv_locations:
                print(f"  • {path}")

    def _initialize_model(self):
        """
        Initialize the Gemini model with fallbacks.
        """
        model_options = [
            "models/gemini-2.0-flash-exp",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
        ]

        for model_name in model_options:
            try:
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ Using model: {model_name}")
                return
            except Exception as e:
                print(f"⚠️  Failed to initialize {model_name}: {e}")
                continue

        raise ValueError("❌ Failed to initialize any Gemini model")

    def _encode_image(self, image_path):
        """
        Encode an image file to base64 for Gemini API.

        Args:
            image_path (str): Path to the image file

        Returns:
            dict: Image data formatted for Gemini API
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        return {"mime_type": "image/png", "data": encoded_string}

    def _load_csv_summary(self, ticker):
        """
        Load and summarize CSV data for the ticker.

        Args:
            ticker (str): Stock ticker symbol

        Returns:
            str: Summary text of the stock data
        """
        csv_file = f"{self.csv_path}{ticker}.csv"

        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file for {ticker} not found at {csv_file}")

        df = pd.read_csv(csv_file)

        # Handle both 'Date' and 'Datetime' column names
        date_column = "Date" if "Date" in df.columns else "Datetime"

        # Get the latest data
        latest_data = df.iloc[-1]

        # Calculate key metrics
        price_change = (latest_data["Close"] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100
        high_6mo = df["High"].max()
        low_6mo = df["Low"].min()
        avg_volume = df["Volume"].mean()

        # Create comprehensive summary
        summary = f"""
Stock Data Summary for {ticker}:
- Total data points: {len(df)}
- Date range: {df[date_column].min()} to {df[date_column].max()}
- Current price: ${latest_data['Close']:.2f}
- Price change from start: {price_change:.2f}%
- 6 month high: ${high_6mo:.2f}
- 6 month low: ${low_6mo:.2f}
- Average volume: {avg_volume:,.0f}

Current Technical Indicators:
- RSI (14): {latest_data['RSI_14']:.2f}
- MACD: {latest_data['MACD_12_26_9']:.4f}
- MACD Histogram: {latest_data['MACDh_12_26_9']:.4f}
- SMA 20: ${latest_data['SMA_20']:.2f}
- SMA 50: ${latest_data['SMA_50']:.2f}

Price vs Moving Averages:
- Price vs SMA 20: {((latest_data['Close'] - latest_data['SMA_20']) / latest_data['SMA_20'] * 100):.2f}%
- Price vs SMA 50: {((latest_data['Close'] - latest_data['SMA_50']) / latest_data['SMA_50'] * 100):.2f}%
- SMA 20 vs SMA 50: {((latest_data['SMA_20'] - latest_data['SMA_50']) / latest_data['SMA_50'] * 100):.2f}%

Recent Performance (last 10 periods):
- High: ${df['High'].tail(10).max():.2f}
- Low: ${df['Low'].tail(10).min():.2f}
- Average Volume: {df['Volume'].tail(10).mean():,.0f}
        """

        return summary

    def generate_report(self, ticker, csv_path=None, graph_paths=None):
        """
        Generate a comprehensive stock report using Gemini 2.5 Pro.

        Args:
            ticker (str): Stock ticker symbol
            csv_path (str, optional): Path to CSV file. If None, uses default path.
            graph_paths (dict, optional): Dictionary of graph paths. If None, uses default paths.
                Expected keys: 'trend', 'macd', 'rsi', 'quantile'

        Returns:
            tuple: (report_text, report_filename) or (error_message, None)
        """
        try:
            # Use provided CSV path or default
            if csv_path is None:
                csv_path = f"{self.csv_path}{ticker}.csv"

            # Load CSV data summary
            data_summary = self._load_csv_summary(ticker)

            # Use provided graph paths or construct defaults
            if graph_paths is None:
                graph_paths = {
                    "trend": f"{self.graphs_path}MAs.png",
                    "macd": f"{self.graphs_path}macd.png",
                    "rsi": f"{self.graphs_path}rsi.png",
                    "quantile": f"{self.graphs_path}{ticker}_quantile_forecast.png",
                }

            # Verify all required files exist
            missing_files = []

            # Check CSV file
            csv_file = f"{self.csv_path}{ticker}.csv"
            if not os.path.exists(csv_file):
                missing_files.append(f"CSV: {csv_file}")

            # Check graph files
            for graph_name, path in graph_paths.items():
                if not os.path.exists(path):
                    missing_files.append(f"{graph_name}: {path}")

            if missing_files:
                error_msg = "❌ Missing required files:\n" + "\n".join(
                    f"  • {file}" for file in missing_files
                )
                error_msg += (
                    "\n\n🔧 Please ensure all files exist before running the report generator."
                )
                print(error_msg)
                return error_msg, None

            # Encode images for Gemini
            encoded_images = {}
            for graph_name, path in graph_paths.items():
                encoded_images[graph_name] = self._encode_image(path)
                print(f"✅ Encoded {graph_name} chart")

            # Create comprehensive prompt using centralized prompt template
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt = get_analysis_prompt(ticker, data_summary, timestamp)

            # Prepare content for Gemini
            content = [prompt]

            # Add images in logical order
            for graph_name in ["trend", "macd", "rsi"]:
                if graph_name in encoded_images:
                    content.append(encoded_images[graph_name])

            print("🤖 Generating comprehensive report with Gemini 2.5 Pro...")

            # Generate content with Gemini
            response = self.model.generate_content(
                content,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Lower temperature for more consistent analysis
                    max_output_tokens=8000,  # Allow for detailed reports
                ),
            )

            # Extract and format the response with better error handling
            if response.parts:
                report = response.text
            else:
                # Handle case where response has no parts (finish_reason issues)
                error_msg = f"❌ Model response blocked. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}"
                print(error_msg)
                return error_msg, None

            # Create reports directory if it doesn't exist
            reports_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports"
            )
            os.makedirs(reports_dir, exist_ok=True)

            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"{reports_dir}/{ticker}_analysis_report_{timestamp}.md"

            with open(report_filename, "w") as f:
                f.write(f"# Professional Stock Analysis Report: {ticker}\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(report)

            print(f"✅ Report saved to: {report_filename}")

            return report, report_filename

        except Exception as e:
            error_msg = f"❌ Error generating report: {str(e)}"
            print(error_msg)
            return error_msg, None

    def print_report(self, ticker):
        """
        Generate and print a stock report to console.
        Assumes CSV data and graph files already exist.

        Args:
            ticker (str): Stock ticker symbol

        Returns:
            str: Path to generated markdown file, or None if failed
        """
        print(f"\n{'='*80}")
        print(f"🏛️  PROFESSIONAL STOCK ANALYSIS REPORT: {ticker.upper()}")
        print(f"{'='*80}")

        result = self.generate_report(ticker)

        if isinstance(result, tuple) and len(result) == 2:
            report, report_filename = result
            print("\n" + report)
            print(f"\n{'='*80}")
            print("📊 Report completed successfully!")
            print("💾 Full report saved in reports/ directory")
            print(f"{'='*80}")

            return report_filename
        else:
            print(result)
            return None


# Example usage and integration with existing main.py
def integrate_with_main():
    """
    Function to integrate Gemini report generation with existing main.py workflow
    """
    try:
        return GeminiStockReportGenerator()  # Use centralized dotenv loading
    except Exception as e:
        print(f"❌ Error initializing Gemini generator: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Get Google AI API key from: https://aistudio.google.com/app/apikey")
        print("2. Create or edit the .env file in project root")
        print("3. Add: GOOGLE_AI_API_KEY=your_actual_api_key")
        print("4. Save the .env file and try again")
        return None


if __name__ == "__main__":
    # Enhanced main execution with better error handling
    import sys

    try:
        # Get ticker from command line argument or use default
        ticker = sys.argv[1] if len(sys.argv) > 1 else "lvmuy"

        print(f"🎯 Generating report for: {ticker}")

        # Initialize the generator (it will handle dotenv loading internally)
        generator = GeminiStockReportGenerator()

        # Generate and print report
        generator.print_report(ticker)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if .env file exists in project root")
        print("2. Verify GOOGLE_AI_API_KEY is set correctly in .env")
        print("3. Get API key from: https://aistudio.google.com/app/apikey")
        print("4. Ensure required CSV and graph files exist")
        print(f"\n📁 Usage: python {os.path.basename(__file__)} [TICKER]")
        print(f"📁 Example: python {os.path.basename(__file__)} LVMUY")
        print(f"📁 Current ticker: {sys.argv[1] if len(sys.argv) > 1 else 'LVMUY'}")

        # Show file requirements for current ticker
        ticker = sys.argv[1] if len(sys.argv) > 1 else "LVMUY"
        print(f"\n📋 Required files for {ticker}:")
        print(f"  • CSV: data/{ticker.lower()}.csv")
        print("  • Graphs: graphs/MAs.png, graphs/macd.png, graphs/rsi.png")
        print(f"  • Forecast: graphs/{ticker}_quantile_forecast.png")
