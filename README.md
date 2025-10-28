# Stock Analysis Report Generator

A passion project that combines my interests in financial markets and software development. Built this to explore how AI can assist in technical analysis, development, and report generation.

## What It Does

Takes a stock ticker, pulls historical data, runs technical analysis, and generates a formatted PDF report using Google's Gemini AI. Not meant for actual trading decisions, more of a proof-of-concept for integrating multiple technologies into a functional pipeline.

**Sample Output**: Enter `NVDA`, get a multi-page PDF with candlestick charts, MACD/RSI indicators, AI-generated analysis, and price forecasts.

## Tech Stack

- **Python 3.11+** - Core language
- **yfinance** - Stock data API (free, no auth needed)
- **pandas/numpy** - Data manipulation
- **matplotlib/mplfinance** - Chart generation
- **scikit-learn** - Quantile regression forecasting
- **Google Gemini 2.5 Pro API** - AI report generation (Ollama coming soon!)
- **ReportLab** - PDF creation from markdown

## What I Learned

- **Quantile Regression**: Implemented probabilistic forecasting instead of point estimates; shows prediction bands for stop losses and risk assessment
- **Financial Data Processing**: Learned the componenets of working with time-series data
- **Multi-modal AI**: Feeding both structured data (CSVs) and images (charts) to Gemini for contextual analysis
- **PDF Generation Pipeline**: Markdown → PDF with embedded images, parsing ai generated outputs


## Setup

```bash
# Clone and create virtual environment
python -m venv stockenv311
source stockenv311/bin/activate  # Windows: stockenv311\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Get a free Gemini API key: https://makersuite.google.com/app/apikey
# Create .env file:
echo "GOOGLE_AI_API_KEY=your_key_here" > .env
```

## Usage

```bash
python code/main.py
```

Enter a ticker (like `AAPL`) and timeframe (like `6mo`). The system will:
1. Download stock data → saves to `CSVs/`
2. Generate technical charts → saves to `graphs/`
3. Run quantile forecasting
4. Send everything to Gemini for analysis
5. Convert markdown report to PDF → saves to `reports/`

**Note**: The Gemini API call can take 30-60 seconds depending on data size.

## Project Structure

```
code/
├── main.py           # Orchestrates the entire pipeline
├── makeCSV.py        # yfinance data fetching
├── makeGraph.py      # Technical indicator charts (MA, MACD, RSI)
├── quantile.py       # Scikit-learn quantile regression model
├── gemini_report.py  # AI report generation
└── pdf_generator.py  # ReportLab PDF conversion

CSVs/      # Raw stock data
graphs/    # Generated charts (auto-embedded in PDFs)
reports/   # Final markdown + PDF outputs
```

## Known Issues

- **API Costs**: Gemini Pro isn't free at scale. Each report uses ~100k tokens.
- **PDF Formatting**: Page breaks can look awkward given too little or too mmuch content.

## Future Plans

- **Ollama Integration**: Want to add local LLM support (Llama 3.1) so people can run this without API keys
- **Better Backtesting**: Add historical accuracy metrics for the quantile forecasts
- **Web Interface**: Flask/Streamlit frontend instead of CLI

## Why This Project?

I'm passionate about financial markets and wanted to build something that reflects that while showcasing technical skills. This project forced me to:
- Work with real-world APIs and messy data
- Integrate machine learning (quantile regression)
- Handle multi-step pipelines with proper error handling
- Generate professional-looking outputs

## Disclaimer

The AI analysis is experimental, the forecasts are probabilistic guesses, and I'm not a financial advisor. Built for learning and demonstration purposes.