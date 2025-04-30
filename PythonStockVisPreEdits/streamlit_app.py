import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
from newsapi import NewsApiClient
import os
from io import BytesIO
from typing import Dict, Any, Optional, Union
import finnhub

# Set page config
st.set_page_config(
    page_title="Stock Visualizer",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    :root {
        --primary-color: #2563eb;
        --secondary-color: #1e40af;
        --background-color: #f8fafc;
        --text-color: #1e293b;
        --error-color: #dc2626;
        --success-color: #059669;
    }

    .stApp {
        background-color: var(--background-color);
    }

    .main .block-container {
        max-width: 1200px;
        padding: 2rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    h1 {
        color: var(--primary-color);
        text-align: center;
    }

    .metric-card {
        background-color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
    }

    .metric-value {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-color);
    }

    .news-block {
        border: 1px solid #e2e8f0;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        display: flex;
        gap: 1rem;
        align-items: flex-start;
    }

    .news-image {
        width: 100px;
        height: 100px;
        object-fit: cover;
        border-radius: 4px;
    }

    .business-summary {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #475569;
    }
    </style>
""", unsafe_allow_html=True)


def format_currency(value: Union[str, float, int]) -> str:
    """Format large numbers with appropriate suffixes (K, M, B, T).
    
    Args:
        value: The number to format
        
    Returns:
        Formatted string with appropriate suffix
    """
    if value == "N/A":
        return str(value)
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
        return f"${value:.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value: Union[str, float]) -> str:
    """Format percentage values.
    
    Args:
        value: The percentage value to format
        
    Returns:
        Formatted percentage string
    """
    if value == "N/A":
        return str(value)
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return str(value)


def create_stock_chart(data: Any, ticker: str) -> BytesIO:
    """Create a stock chart using mplfinance.
    
    Args:
        data: Stock data from yfinance
        ticker: Stock ticker symbol
        
    Returns:
        BytesIO buffer containing the chart image
    """
    plt.ioff()
    fig = plt.figure(figsize=(10, 6))
    
    mpf.plot(data, 
            type='candle',
            style='charles',
            title=f"{ticker} — Last 30 Days",
            ylabel="Price (USD)",
            volume=False,
            figsize=(10, 6),
            returnfig=True)
    
    plt.title(f"{ticker} — Last 30 Days", pad=20, y=1.02)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf


def get_stock_info(ticker: str) -> tuple[Optional[Any], Optional[Dict], Optional[str]]:
    """Fetch stock data and information.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Tuple of (stock data, stock info, error message)
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")
        
        if data.empty:
            return None, None, f"No data found for ticker: {ticker}. Please check the ticker symbol and try again."
        
        info = stock.info
        if not info:
            return None, None, f"Could not retrieve information for ticker: {ticker}. Please check the ticker symbol and try again."
            
        return data, info, None
    except Exception as e:
        return None, None, f"Error fetching data: {str(e)}"


def display_company_header(info: Dict, ticker: str) -> None:
    """Display the company header with logo and name.
    
    Args:
        info: Stock information dictionary
        ticker: Stock ticker symbol
    """
    logo_url = info.get('logo_url', '') or info.get('logo', '')
    if not logo_url and info.get('website'):
        logo_url = f"{info['website']}/favicon.ico"
    
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin: 1rem 0;">
    """, unsafe_allow_html=True)
    
    if logo_url:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem;">
                <img src="{logo_url}" style="width: 50px; height: 50px; object-fit: contain;">
                <h3 style="margin: 0; padding: 0; line-height: 1;">{info.get('longName', ticker)} ({ticker})</h3>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <h3 style="margin: 0; padding: 0; line-height: 1;">{info.get('longName', ticker)} ({ticker})</h3>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def display_financial_metrics(info: Dict, ticker: str) -> None:
    """Display financial metrics in a grid layout.
    
    Args:
        info: Stock information dictionary
        ticker: Stock ticker symbol
    """
    current_price = info.get('currentPrice', 0)
    previous_close = info.get('previousClose', 0)
    price_change = current_price - previous_close
    price_change_percent = (price_change / previous_close * 100) if previous_close else 0
    
    metrics = {
        "Company": info.get("longName", ticker),
        "Current Price": f"{format_currency(current_price)} ({price_change:+.2f} {price_change_percent:+.2f}%)",
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
    
    st.markdown("### Financial Metrics")
    cols = st.columns(4)
    
    for i, (metric, value) in enumerate(metrics.items()):
        with cols[i % 4]:
            color = 'var(--success-color)' if metric == "Current Price" and price_change >= 0 else 'var(--error-color)' if metric == "Current Price" and price_change < 0 else 'var(--text-color)'
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{metric}</div>
                    <div class="metric-value" style="color: {color}">{value}</div>
                </div>
            """, unsafe_allow_html=True)


def display_news_articles(company_name: str, ticker: str) -> None:
    """Display news articles related to the company.
    
    Args:
        company_name: Full name of the company
        ticker: Stock ticker symbol
    """
    try:
        newsapi = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))
        
        # Try with financial terms first
        news_data = newsapi.get_everything(
            q=f"({company_name} OR {ticker}) AND (stock OR shares OR earnings OR financial OR market OR investor)",
            language="en",
            sort_by="publishedAt",
            page_size=5
        )
        
        news_articles = news_data.get("articles", [])
        
        # If no results, try without financial terms
        if not news_articles:
            news_data = newsapi.get_everything(
                q=f"{company_name} OR {ticker}",
                language="en",
                sort_by="publishedAt",
                page_size=5
            )
            news_articles = news_data.get("articles", [])
        
        for article in news_articles:
            st.markdown(f"""
                <div class="news-block">
                    <img src="{article.get('urlToImage', '')}" class="news-image" onerror="this.style.display='none'">
                    <div class="news-content">
                        <h3><a href="{article['url']}" target="_blank">{article['title']}</a></h3>
                        <p>{article['description']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")


def get_related_stocks(ticker: str, max_results: int = 6) -> list[str]:
    """Get related stocks based on industry and sector.
    
    Args:
        ticker: Stock ticker symbol
        max_results: Maximum number of related stocks to return
        
    Returns:
        List of related stock tickers
    """
    api_key = os.getenv('FINNHUB_API_KEY', '')
    if not api_key:
        st.error("Finnhub API key not set. Please export FINNHUB_API_KEY.")
        return []
    client = finnhub.Client(api_key=api_key)
    try:
        peers = client.company_peers(ticker)
        # Filter out the current stock and limit results
        return [peer for peer in peers if peer != ticker][:max_results]
    except Exception as e:
        st.error(f"Error fetching peers from Finnhub: {e}")
        return []


def display_related_stocks(related_stocks: list[str]) -> None:
    """Display related stocks as buttons.
    
    Args:
        related_stocks: List of related stock tickers
    """
    st.markdown("### Related Stocks")
    
    if not related_stocks:
        st.info("No related stocks found for this company.")
        return
        
    cols = st.columns(len(related_stocks))
    
    for i, ticker in enumerate(related_stocks):
        if cols[i].button(ticker, key=f"related_{ticker}"):
            st.session_state.ticker = ticker
            st.rerun()


def main():
    """Main function to run the Streamlit application."""
    st.title("Stock Visualizer")
    
    # Ticker buttons
    popular_tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "NVDA"]
    cols = st.columns(len(popular_tickers))
    for i, ticker_symbol in enumerate(popular_tickers):
        if cols[i].button(ticker_symbol, key=f"ticker_{i}"):
            st.session_state.ticker = ticker_symbol
            st.rerun()

    # Search form
    with st.form("search_form"):
        ticker = st.text_input("Enter Stock Ticker", value=st.session_state.get("ticker", ""))
        submit = st.form_submit_button("Search")

    if submit or st.session_state.get("ticker"):
        ticker = ticker.upper() if submit else st.session_state.ticker
        st.session_state.ticker = ticker
        
        data, info, error = get_stock_info(ticker)
        if error:
            st.warning(error)
            return
            
        display_company_header(info, ticker)
        
        # Display related stocks
        related_stocks = get_related_stocks(ticker)
        display_related_stocks(related_stocks)
        
        with st.expander("Business Summary", expanded=False):
            st.markdown(f"""
                <div class="business-summary">
                    {info.get("longBusinessSummary", "No business summary available.")}
                </div>
            """, unsafe_allow_html=True)
        
        chart_buffer = create_stock_chart(data, ticker)
        st.image(chart_buffer, use_container_width=True)
        
        display_financial_metrics(info, ticker)
        
        st.markdown("### Latest News")
        display_news_articles(info.get("longName", ticker), ticker)


if __name__ == "__main__":
    main()
