#!/usr/bin/env python3
"""
PDF Report Generator for Stock Analysis
Converts markdown reports to formatted PDFs with embedded graphs
"""

import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import markdown
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

class PDFReportGenerator:
    """
    A class to convert markdown stock analysis reports to formatted PDFs
    with embedded technical analysis charts.
    """
    
    def __init__(self, graphs_path=None):
        """
        Initialize the PDF generator.
        
        Args:
            graphs_path (str): Path to the graphs directory
        """
        if graphs_path is None:
            # Use relative path from project root
            self.graphs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "graphs")
        else:
            self.graphs_path = graphs_path
        self.setup_styles()
    
    def setup_styles(self):
        """Set up custom styles for the PDF document."""
        self.styles = getSampleStyleSheet()
        
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#1a1a1a'),
            fontName='Helvetica-Bold'
        ))
        
        # Custom subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=HexColor('#4a4a4a'),
            fontName='Helvetica'
        ))
        
        # Custom header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=HexColor('#2c5282'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=HexColor('#2c5282'),
            borderPadding=8
        ))
        
        # Custom subheader style
        self.styles.add(ParagraphStyle(
            name='CustomSubheader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=15,
            textColor=HexColor('#2d3748'),
            fontName='Helvetica-Bold'
        ))
        
        # Custom body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#2d3748'),
            fontName='Helvetica'
        ))
        
        # Custom bullet style
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10,
            textColor=HexColor('#2d3748'),
            fontName='Helvetica'
        ))
        
        # Executive summary style
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            textColor=HexColor('#1a1a1a'),
            fontName='Helvetica',
            backColor=HexColor('#f7fafc'),
            borderWidth=1,
            borderColor=HexColor('#e2e8f0'),
            borderPadding=10
        ))
        
        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=HexColor('#065f46'),
            fontName='Helvetica-Bold',
            backColor=HexColor('#d1fae5'),
            borderWidth=2,
            borderColor=HexColor('#065f46'),
            borderPadding=10
        ))
    
    def parse_markdown(self, markdown_text):
        """
        Parse markdown text and extract structured content.
        
        Args:
            markdown_text (str): Raw markdown text
            
        Returns:
            dict: Parsed content structure
        """
        # Convert markdown to HTML
        html = markdown.markdown(markdown_text)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract content sections
        content = {
            'title': '',
            'subtitle': '',
            'sections': []
        }
        
        # Find title
        h1 = soup.find('h1')
        if h1:
            content['title'] = h1.get_text().strip()
        
        # Find subtitle (generated on line)
        generated_line = soup.find(string=re.compile(r'Generated on:'))
        if generated_line:
            content['subtitle'] = generated_line.strip()
        
        # Parse sections
        current_section = None
        current_subsection = None
        
        for element in soup.find_all(['h2', 'h3', 'p', 'ul', 'li']):
            if element.name == 'h2':
                if current_section:
                    content['sections'].append(current_section)
                current_section = {
                    'title': element.get_text().strip(),
                    'content': [],
                    'subsections': []
                }
                current_subsection = None
                
            elif element.name == 'h3':
                if current_section:
                    if current_subsection:
                        current_section['subsections'].append(current_subsection)
                    current_subsection = {
                        'title': element.get_text().strip(),
                        'content': []
                    }
                    
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    if current_subsection:
                        current_subsection['content'].append(('paragraph', text))
                    elif current_section:
                        current_section['content'].append(('paragraph', text))
                        
            elif element.name == 'ul':
                items = [li.get_text().strip() for li in element.find_all('li')]
                if current_subsection:
                    current_subsection['content'].append(('bullet_list', items))
                elif current_section:
                    current_section['content'].append(('bullet_list', items))
        
        # Add the last section
        if current_section:
            if current_subsection:
                current_section['subsections'].append(current_subsection)
            content['sections'].append(current_section)
        
        return content
    
    def add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(HexColor('#2c5282'))
        canvas.drawString(50, letter[1] - 50, "Professional Stock Analysis Report")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(HexColor('#718096'))
        canvas.drawString(50, 30, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        canvas.drawRightString(letter[0] - 50, 30, f"Page {doc.page}")
        
        canvas.restoreState()
    
    def add_charts_section(self, story, ticker):
        """Add technical analysis charts to the PDF."""
        # Page break before first chart
        story.append(PageBreak())
        
        # Charts section header
        story.append(Paragraph("TECHNICAL ANALYSIS CHARTS", self.styles['CustomHeader']))
        story.append(Spacer(1, 12))
        
        # Chart descriptions and images
        charts = [
            {
                'title': 'Price Trend with Moving Averages',
                'filename': 'MAs.png',
                'description': 'Candlestick chart showing price action with SMA 20 and SMA 50 overlays. This chart reveals the overall price trend, support/resistance levels, and moving average relationships.'
            },
            {
                'title': 'MACD Momentum Indicator',
                'filename': 'macd.png',
                'description': 'MACD line, signal line, and histogram analysis. Shows momentum changes, signal line crossovers, and divergence patterns.'
            },
            {
                'title': 'RSI Relative Strength Index',
                'filename': 'rsi.png',
                'description': 'RSI indicator showing overbought (>70) and oversold (<30) conditions. Helps identify potential reversal points.'
            },
            {
                'title': 'Quantile Forecast Model',
                'filename': f'{ticker}_quantile_forecast.png',
                'description': 'Machine learning-based price forecast with confidence bands. Shows expected price ranges and probability assessments.'
            }
        ]
        
        for i, chart in enumerate(charts):
            chart_path = os.path.join(self.graphs_path, chart['filename'])
            
            # Page break before each chart (except the first one, since we already have charts section header)
            if i > 0:
                story.append(PageBreak())
                story.append(Paragraph("TECHNICAL ANALYSIS CHARTS", self.styles['CustomHeader']))
                story.append(Spacer(1, 12))
            
            if os.path.exists(chart_path):
                # Chart title
                story.append(Paragraph(f"<b>{chart['title']}</b>", self.styles['CustomSubheader']))
                story.append(Spacer(1, 6))
                
                # Chart description
                story.append(Paragraph(chart['description'], self.styles['CustomBody']))
                story.append(Spacer(1, 10))
                
                # Chart image
                try:
                    img = Image(chart_path, width=6*inch, height=4*inch)
                    story.append(img)
                    story.append(Spacer(1, 20))
                except Exception as e:
                    story.append(Paragraph(f"<i>Chart could not be loaded: {str(e)}</i>", self.styles['CustomBody']))
                    story.append(Spacer(1, 10))
            else:
                story.append(Paragraph(f"<b>{chart['title']}</b>", self.styles['CustomSubheader']))
                story.append(Spacer(1, 6))
                story.append(Paragraph(f"<i>Chart not found: {chart['filename']}</i>", self.styles['CustomBody']))
                story.append(Spacer(1, 10))
    
    def convert_to_pdf(self, markdown_file, output_file=None):
        """
        Convert markdown report to PDF.
        
        Args:
            markdown_file (str): Path to the markdown file
            output_file (str, optional): Output PDF file path
            
        Returns:
            str: Path to the generated PDF file
        """
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(f"Markdown file not found: {markdown_file}")
        
        # Generate output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(markdown_file))[0]
            output_dir = os.path.dirname(markdown_file)
            output_file = os.path.join(output_dir, f"{base_name}.pdf")
        
        # Read markdown content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Parse markdown
        content = self.parse_markdown(markdown_content)
        
        # Extract ticker from filename or content
        ticker = self.extract_ticker(markdown_file, content)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=80,
            bottomMargin=50
        )
        
        # Build story
        story = []
        
        # Title page
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(content['title'], self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(content['subtitle'], self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Confidentiality notice
        story.append(Paragraph(
            "<b>CONFIDENTIAL | FOR INSTITUTIONAL & EXPERIENCED RETAIL USE ONLY</b>", 
            self.styles['CustomSubtitle']
        ))
        story.append(Spacer(1, 1*inch))
        
        # Add charts section first
        self.add_charts_section(story, ticker)
        
        # Add content sections
        for section in content['sections']:
            # Add page break before specific sections (checking both section title and subsection titles)
            section_needs_pagebreak = False
            
            # Check main section title
            if ('EXECUTIVE SUMMARY' in section['title'].upper() or
                'INVESTMENT STRATEGY' in section['title'].upper() or 
                'PRICE TARGETS' in section['title'].upper()):
                section_needs_pagebreak = True
            
            # Check subsection titles
            for subsection in section['subsections']:
                if ('EXECUTIVE SUMMARY' in subsection['title'].upper() or
                    'INVESTMENT STRATEGY' in subsection['title'].upper() or 
                    'PRICE TARGETS' in subsection['title'].upper()):
                    section_needs_pagebreak = True
                    break
            
            if section_needs_pagebreak:
                story.append(PageBreak())
            
            # Section header
            story.append(Paragraph(section['title'], self.styles['CustomHeader']))
            story.append(Spacer(1, 12))
            
            # Section content
            for content_type, content_data in section['content']:
                if content_type == 'paragraph':
                    # Special styling for executive summary
                    if 'EXECUTIVE SUMMARY' in section['title']:
                        story.append(Paragraph(content_data, self.styles['ExecutiveSummary']))
                    else:
                        story.append(Paragraph(content_data, self.styles['CustomBody']))
                elif content_type == 'bullet_list':
                    for item in content_data:
                        story.append(Paragraph(f"• {item}", self.styles['CustomBullet']))
            
            # Subsections - THIS IS WHERE WE NEED THE PAGE BREAKS
            for i, subsection in enumerate(section['subsections']):
                # Add page break before specific subsections (but not the first one)
                if (i > 0 and  # Don't add page break before the first subsection
                    ('EXECUTIVE SUMMARY' in subsection['title'].upper() or
                     'INVESTMENT STRATEGY' in subsection['title'].upper() or 
                     'PRICE TARGETS' in subsection['title'].upper())):
                    story.append(PageBreak())
                
                story.append(Paragraph(subsection['title'], self.styles['CustomSubheader']))
                story.append(Spacer(1, 8))
                
                for content_type, content_data in subsection['content']:
                    if content_type == 'paragraph':
                        # Special styling for executive summary
                        if 'EXECUTIVE SUMMARY' in subsection['title']:
                            story.append(Paragraph(content_data, self.styles['ExecutiveSummary']))
                        else:
                            story.append(Paragraph(content_data, self.styles['CustomBody']))
                    elif content_type == 'bullet_list':
                        for item in content_data:
                            story.append(Paragraph(f"• {item}", self.styles['CustomBullet']))
            
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story, onFirstPage=self.add_header_footer, onLaterPages=self.add_header_footer)
        
        return output_file
    
    def extract_ticker(self, markdown_file, content):
        """Extract ticker symbol from filename or content."""
        # Try to extract from filename first
        filename = os.path.basename(markdown_file)
        ticker_match = re.search(r'^([A-Za-z0-9\-]{1,20})_analysis_report', filename)
        if ticker_match:
            return ticker_match.group(1).upper()  # Convert to uppercase for consistency
        
        # Try to extract from content
        title = content.get('title', '')
        ticker_match = re.search(r':\s*([A-Za-z0-9\-]{1,20})\s*$', title)
        if ticker_match:
            return ticker_match.group(1).upper()  # Convert to uppercase for consistency
        
        return 'UNKNOWN'
    
    def batch_convert(self, reports_dir, output_dir=None):
        """
        Convert all markdown reports in a directory to PDF.
        
        Args:
            reports_dir (str): Directory containing markdown reports
            output_dir (str, optional): Output directory for PDFs
            
        Returns:
            list: List of generated PDF files
        """
        if output_dir is None:
            output_dir = reports_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        pdf_files = []
        markdown_files = [f for f in os.listdir(reports_dir) if f.endswith('.md')]
        
        for md_file in markdown_files:
            md_path = os.path.join(reports_dir, md_file)
            pdf_name = os.path.splitext(md_file)[0] + '.pdf'
            pdf_path = os.path.join(output_dir, pdf_name)
            
            try:
                self.convert_to_pdf(md_path, pdf_path)
                pdf_files.append(pdf_path)
                print(f"✅ Converted {md_file} → {pdf_name}")
            except Exception as e:
                print(f"❌ Failed to convert {md_file}: {str(e)}")
        
        return pdf_files

# Integration function for main pipeline
def create_pdf_report(markdown_file, output_file=None):
    """
    Create PDF report from markdown file.
    
    Args:
        markdown_file (str): Path to markdown file
        output_file (str, optional): Output PDF path
        
    Returns:
        str: Path to generated PDF file
    """
    try:
        generator = PDFReportGenerator()
        pdf_file = generator.convert_to_pdf(markdown_file, output_file)
        print(f"✅ PDF report generated: {pdf_file}")
        return pdf_file
    except Exception as e:
        print(f"❌ PDF generation failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    try:
        generator = PDFReportGenerator()
        
        # Convert all markdown reports to PDF
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
        pdf_files = generator.batch_convert(reports_dir)
        
        print(f"\\n✅ Successfully converted {len(pdf_files)} reports to PDF:")
        for pdf_file in pdf_files:
            print(f"   • {os.path.basename(pdf_file)}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\\n🔧 Setup Instructions:")
        print("1. Install required packages:")
        print("   pip install reportlab markdown beautifulsoup4")
        print("2. Ensure markdown reports exist in reports/ directory")
        print("3. Run this script again")
