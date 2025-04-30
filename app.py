from flask import Flask, render_template, request
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
import io
import base64
from newsapi import NewsApiClient
import os
import mplfinance as mpf

app = Flask(__name__)

def format_currency(value):
    """Format large numbers with appropriate suffixes"""
    if value == "N/A":
        return value
    try:
        value = float(value)
        if abs(value) >= 1e12:
            return f"${value/1e12:.2f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:.2f}"
    except:
        return str(value)

def format_percentage(value):
    """Format percentage values"""
    if value == "N/A":
        return value
    try:
        return f"{float(value):.2f}%"
    except:
        return str(value)

def create_stock_chart(data, ticker):
    """Create a stock chart safely in a non-GUI context"""
    plt.ioff()  # Turn off interactive mode
    fig = plt.figure(figsize=(10, 6))
    mpf.plot(data, type='candle', style='charles',
            title=f"{ticker} — Last 30 Days",
            ylabel="Price (USD)",
            volume=False,
            figsize=(10, 6),
            savefig=dict(fname='temp.png', dpi=100, bbox_inches='tight'))
    plt.close(fig)  # Close the figure to free memory
    
    # Read the saved plot and encode to base64
    with open('temp.png', 'rb') as img_file:
        chart = base64.b64encode(img_file.read()).decode("ascii")
    os.remove('temp.png')
    return chart

@app.route("/", methods=["GET", "POST"])
def index():
    chart = None
    ticker = None
    financial_data = {}
    news_articles = []
    business_summary = ""

    if request.method == "POST":
        # 1. Get ticker symbol from form
        ticker = request.form.get("ticker", "").upper()

        # 2. Fetch stock data
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")
        if not data.empty:
            # 3. Get financial metrics
            info = stock.info
            # Get logo URL - yfinance provides it in the 'logo_url' field
            logo_url = info.get('logo_url', '')
            if not logo_url:
                # Try alternative field names
                logo_url = info.get('logo', '')
            if not logo_url:
                # Try to construct the logo URL from the website
                website = info.get('website', '')
                if website:
                    # Try to get the favicon as a fallback
                    logo_url = f"{website}/favicon.ico"
            
            print(f"Logo URL for {ticker}: {logo_url}")  # Debug print
            
            # Calculate price change
            current_price = info.get('currentPrice', 0)
            previous_close = info.get('previousClose', 0)
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close * 100) if previous_close else 0
            
            financial_data = {
                "Company Name": info.get("longName", ticker),
                "Logo": logo_url,
                "Current Price": {
                    "value": format_currency(current_price),
                    "change": price_change,
                    "change_percent": price_change_percent,
                    "is_positive": price_change >= 0
                },
                "Market Cap": format_currency(info.get("marketCap", "N/A")),
                "52 Week High": format_currency(info.get("fiftyTwoWeekHigh", "N/A")),
                "52 Week Low": format_currency(info.get("fiftyTwoWeekLow", "N/A")),
                "Volume": format_currency(info.get("volume", "N/A")),
                "Average Volume": format_currency(info.get("averageVolume", "N/A")),
                "P/E Ratio": format_currency(info.get("trailingPE", "N/A")),
                "Forward P/E": format_currency(info.get("forwardPE", "N/A")),
                "PEG Ratio": format_currency(info.get("pegRatio", "N/A")),
                "Dividend Yield": format_percentage(info.get("dividendYield", "N/A")),
                "Beta": format_currency(info.get("beta", "N/A")),
                "Profit Margins": format_percentage(info.get("profitMargins", "N/A")),
                "Revenue Growth": format_percentage(info.get("revenueGrowth", "N/A")),
                "Earnings Growth": format_percentage(info.get("earningsGrowth", "N/A")),
                "ROE": format_percentage(info.get("returnOnEquity", "N/A")),
                "ROA": format_percentage(info.get("returnOnAssets", "N/A")),
                "Debt to Equity": format_currency(info.get("debtToEquity", "N/A")),
                "Operating Cash Flow": format_currency(info.get("operatingCashflow", "N/A")),
                "Free Cash Flow": format_currency(info.get("freeCashflow", "N/A")),
            }

            # 4. Plot clean candlestick chart
            chart = create_stock_chart(data, ticker)

            # 5. Get business summary
            business_summary = info.get("longBusinessSummary", "No business summary available.")

            # 6. Fetch news from NewsAPI
            try:
                # Get company's full name for better search results
                company_name = info.get("longName", ticker)
                
                # Initialize NewsAPI client
                newsapi = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))
                
                # Search for news using both company name and ticker with more specific terms
                news_data = newsapi.get_everything(
                    q=f"({company_name} OR {ticker}) AND (stock OR shares OR earnings OR financial OR market OR investor)",
                    language="en",
                    sort_by="publishedAt",
                    page_size=5
                )
                news_articles = news_data.get("articles", [])
                
                # If no articles found with specific terms, try a broader search
                if not news_articles:
                    news_data = newsapi.get_everything(
                        q=f"{company_name} OR {ticker}",
                        language="en",
                        sort_by="publishedAt",
                        page_size=5
                    )
                    news_articles = news_data.get("articles", [])
                    
                # Filter out irrelevant articles
                news_articles = [
                    article for article in news_articles
                    if any(keyword in article['title'].lower() or keyword in article['description'].lower()
                          for keyword in ['stock', 'shares', 'earnings', 'financial', 'market', 'investor', 'trading'])
                ]
                
            except Exception as e:
                print(f"Error fetching news: {e}")
                news_articles = []

    return render_template("index.html", 
                         chart=chart, 
                         ticker=ticker, 
                         financial_data=financial_data, 
                         news_articles=news_articles,
                         business_summary=business_summary)

if __name__ == "__main__":
    app.run(debug=True)
