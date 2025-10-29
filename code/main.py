from makeCSV import StockDataHandler
from makeGraph import GraphGenerator
from quantile import QuantileForecaster
from gemini_report import integrate_with_main
from pdf_generator import create_pdf_report

def run_pipeline():
    ticker = input("Enter a ticker for stock data: ")

    # Initialize all components
    data_handler = StockDataHandler(ticker)
    graph_generator = GraphGenerator(ticker)
    quantile_forecaster = QuantileForecaster(ticker)

    # Generate longer period data for quantile analysis
    print("[*] Generating Quantile Predictions...")
    data_handler.fetch_and_prepare_data(period="2y", interval="4h")
    data_handler.clean_csv()
    quantile_forecaster.run()

    # --- User Input for Main Report ---
    period = input("Enter a time frame for the stock (1d, 5d, 1mo, 3mo, 6mo, 1y): ")
    if period == "1d":
        interval = "2m"
    elif period == "5d":
        interval = "15m"
    elif period == "1mo":
        interval = "1h"
    elif period == "3mo":
        interval = "4h"
    elif period == "6mo":
        interval = "1d"
    else:
        interval = "1d"

    print("[*] Generating CSV...")
    data_handler.fetch_and_prepare_data(period=period, interval=interval)

    print("[*] Plotting data...")
    graph_generator.generate_all()

    # Generate AI-powered investment report
    print("[*] Initializing AI Report Generator...")
    ai_generator = integrate_with_main()
    
    markdown_file = None
    if ai_generator:
        print("[*] Generating AI-powered investment report...")
        markdown_file = ai_generator.print_report(ticker)
    else:
        print("[!] AI reporting not available - continuing without it")
        print("    To enable AI reports, set up your Google AI API key in .env file")

    # Generate PDF report from markdown
    if markdown_file:
        print("[*] Converting report to PDF...")
        pdf_file = create_pdf_report(markdown_file)
        if pdf_file:
            print(f"✅ PDF report generated: {pdf_file}")
        else:
            print("❌ PDF generation failed")

    print("\n🎉 Pipeline completed successfully!")
    if ai_generator:
        print("   • reports/ - AI-generated investment reports")
        if markdown_file:
            print("   • PDF reports with embedded technical charts")

    
if __name__ == "__main__":
    run_pipeline()
