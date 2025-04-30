# Stock Market Visualizer

A web application for visualizing stock market data using Streamlit.

## Overview

This application provides a user-friendly interface for viewing and analyzing stock market data, including:

- Real-time stock price charts
- Company information and financial metrics
- Latest news articles
- Related stocks analysis

## Features

- Interactive stock charts with technical indicators
- Comprehensive financial metrics display
- Real-time news integration
- Related stocks suggestions
- Responsive and modern UI

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/stock-visualizer.git
cd stock-visualizer
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory with your API keys:

```
NEWS_API_KEY=your_news_api_key
FINNHUB_API_KEY=your_finnhub_api_key
```

To get a NewsAPI key:

1. Go to [NewsAPI.org](https://newsapi.org/)
2. Sign up for a free account
3. Once logged in, go to your dashboard
4. Copy your API key
5. Add it to your `.env` file as shown above

To get a Finnhub API key:

1. Go to [Finnhub.io](https://finnhub.io/)
2. Sign up for a free account
3. Once logged in, go to your dashboard
4. Copy your API key
5. Add it to your `.env` file as shown above

## Usage

Run the Streamlit application:

```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser.

## Features in Detail

### Stock Visualization

- Interactive candlestick charts
- Multiple time period options
- Technical indicators
- Volume analysis

### Financial Metrics

- Current price and price changes
- Market capitalization
- P/E ratios
- Dividend information
- Key financial ratios

### News Integration

- Latest company news
- Financial market updates
- Related industry news

### Related Stocks

- Industry peers
- Competitor analysis
- Sector performance comparison

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Dependencies

- Streamlit
- yfinance
- matplotlib
- mplfinance
- newsapi
- finnhub
