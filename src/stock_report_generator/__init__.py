"""
Stock Report Generator

A comprehensive tool for generating stock analysis reports with data visualization,
quantile analysis, and AI-powered insights using Google's Gemini API.
"""

__version__ = "1.0.0"

from .gemini_report import GeminiStockReportGenerator
from .makeCSV import StockDataHandler
from .makeGraph import GraphGenerator
from .pdf_generator import PDFReportGenerator
from .quantile import QuantileForecaster

__all__ = [
    "StockDataHandler",
    "GraphGenerator",
    "QuantileForecaster",
    "GeminiStockReportGenerator",
    "PDFReportGenerator",
]
