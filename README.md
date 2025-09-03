# Professional Stock Analysis System

A comprehensive AI-powered stock analysis system that generates professional investment reports with technical analysis charts and converts them to formatted PDFs. The system integrates Gemini 2.5 Pro AI to create institutional-grade reports suitable for experienced retail and institutional investors.

## Features

### 🔥 Core Capabilities
- **Stock Data Fetching**: Retrieves real-time and historical stock data using yfinance
- **Technical Analysis**: Generates professional charts including:
  - Moving Averages (SMA 20, SMA 50) with candlestick charts
  - MACD (Moving Average Convergence Divergence) indicators
  - RSI (Relative Strength Index) analysis
  - Quantile forecasting with machine learning models
- **AI-Powered Analysis**: Uses Gemini 2.5 Pro to generate comprehensive investment reports
- **PDF Generation**: Converts markdown reports to professionally formatted PDFs with embedded charts

### 📊 Technical Analysis Charts
- **Price Trend Analysis**: Candlestick charts with moving averages overlays
- **Momentum Indicators**: MACD line, signal line, and histogram analysis
- **Strength Indicators**: RSI showing overbought/oversold conditions
- **Predictive Modeling**: Quantile forecasting with confidence bands

### 🤖 AI Report Generation
- **Professional Analysis**: Institutional-grade investment reports
- **Technical Insights**: Detailed chart pattern analysis and trend identification
- **Risk Assessment**: Comprehensive risk analysis with scenario planning
- **Actionable Recommendations**: Specific buy/sell/hold recommendations with price targets

### 📄 PDF Report Features
- **Professional Formatting**: Clean, institutional-style document layout
- **Embedded Charts**: All technical analysis charts included in the PDF
- **Structured Content**: Executive summary, technical analysis, investment strategy, and risk assessment
- **Confidentiality Markings**: Appropriate disclaimers for institutional use

## Installation

### Prerequisites
- Python 3.11+
- Google AI API Key (for Gemini 2.5 Pro)

### Setup Instructions

1. **Clone and Setup Environment**
   ```bash
   cd Downloads/repo
   python -m venv stockenv311
   source stockenv311/bin/activate  # On Windows: stockenv311\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install yfinance pandas numpy matplotlib mplfinance seaborn scikit-learn
   pip install google-generativeai python-dotenv
   pip install reportlab markdown beautifulsoup4
   ```

3. **Configure API Key**
   - Get your Google AI API key from: https://makersuite.google.com/app/apikey
   - Create a `.env` file in the project root:
   ```
   GOOGLE_AI_API_KEY=your_actual_api_key_here
   ```

## Usage

### Basic Usage
```bash
python code/main.py
```

Follow the prompts to:
1. Enter a stock ticker symbol (e.g., NVDA, AAPL, MSFT)
2. Select a time frame (1d, 5d, 1mo, 3mo, 6mo, 1y)

The system will:
- Fetch stock data and generate CSV files
- Create technical analysis charts
- Generate quantile forecasts
- Produce AI-powered investment reports
- Convert reports to PDF format

### Advanced Usage

#### Generate Reports for Specific Stocks
```python
from code.gemini_report import GeminiStockReportGenerator
from code.pdf_generator import create_pdf_report

# Initialize the generator
generator = GeminiStockReportGenerator()

# Generate report for specific ticker
markdown_file = generator.print_report("NVDA")

# Convert to PDF
pdf_file = create_pdf_report(markdown_file)
```

#### Batch Process Multiple Stocks
```python
from code.pdf_generator import PDFReportGenerator

# Initialize PDF generator
pdf_gen = PDFReportGenerator()

# Convert all markdown reports to PDF
generated_pdfs = pdf_gen.batch_convert_reports()
```

## File Structure

```
repo/
├── code/
│   ├── main.py              # Main pipeline orchestrator
│   ├── makeCSV.py           # Stock data fetching
│   ├── makeGraph.py         # Technical analysis chart generation
│   ├── quantile.py          # Quantile forecasting model
│   ├── gemini_report.py     # AI report generation
│   ├── pdf_generator.py     # PDF conversion system
│   └── cleanCSVs.py         # Data cleaning utilities
├── CSVs/                    # Stock data files
├── graphs/                  # Technical analysis charts
├── reports/                 # Generated markdown and PDF reports
├── .env                     # API key configuration
└── README.md               # This file
```

## Output Files

### Generated Reports
- **Markdown Reports**: `reports/{TICKER}_analysis_report_{timestamp}.md`
- **PDF Reports**: `reports/{TICKER}_analysis_report_{timestamp}.pdf`

### Technical Charts
- **Moving Averages**: `graphs/MAs.png`
- **MACD Analysis**: `graphs/macd.png`
- **RSI Analysis**: `graphs/rsi.png`
- **Quantile Forecast**: `graphs/{TICKER}_quantile_forecast.png`

## Report Content

### Executive Summary
- Current market position and key takeaways
- Overall investment recommendation
- Price targets and time horizons

### Technical Analysis
- Price action and trend analysis
- Moving average analysis
- Momentum indicators (MACD, RSI)
- Support and resistance levels

### Investment Strategy
- Entry and exit strategies
- Risk management recommendations
- Position sizing guidelines

### Risk Assessment
- Technical risks and pattern failures
- Market context and sector considerations
- Volatility and correlation analysis

### Price Targets & Scenarios
- Bull case, base case, and bear case scenarios
- Probability-weighted price targets
- Catalyst identification

## API Integration

### Gemini 2.5 Pro Features
- **Advanced Analysis**: Utilizes Google's most capable AI model
- **Multi-Modal Input**: Processes both CSV data and chart images
- **Professional Output**: Generates institutional-grade investment reports
- **Customizable Prompts**: Tailored for financial analysis and technical trading

### Configuration
```python
# Environment variable setup
GOOGLE_AI_API_KEY=your_api_key_here

# Model configuration
model = genai.GenerativeModel('models/gemini-2.5-pro')
```

## Error Handling

The system includes comprehensive error handling for:
- Missing API keys
- Invalid stock symbols
- Data fetching failures
- Chart generation errors
- PDF conversion issues

## Security Features

- **API Key Protection**: Environment variable storage
- **Confidentiality Markings**: Appropriate disclaimers on reports
- **Secure File Handling**: Proper file permissions and access controls

## Performance Optimization

- **Efficient Data Processing**: Optimized pandas operations
- **Image Compression**: Proper chart sizing for PDF embedding
- **Memory Management**: Cleanup of temporary files and variables

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your Google AI API key is valid
   - Check that the `.env` file is properly configured
   - Verify API key permissions and quotas

2. **Data Fetching Issues**
   - Check internet connection
   - Verify stock ticker symbols are valid
   - Ensure yfinance is properly installed

3. **PDF Generation Problems**
   - Install required packages: `pip install reportlab markdown beautifulsoup4`
   - Check file permissions in the reports directory
   - Verify chart files exist in the graphs directory

### Debug Mode
To enable debug output, set environment variable:
```bash
export DEBUG=1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with financial regulations and API terms of service when using in production environments.

## Disclaimer

This software is for informational purposes only and does not constitute financial advice. All investment decisions should be made with careful consideration of individual risk tolerance and financial goals. Past performance is not indicative of future results.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Ensure all dependencies are properly installed
4. Verify API key configuration

## Version History

- **v1.0.0**: Initial release with basic stock analysis
- **v2.0.0**: Added AI report generation with Gemini 2.5 Pro
- **v2.1.0**: Integrated PDF generation system
- **v2.2.0**: Enhanced error handling and professional formatting
