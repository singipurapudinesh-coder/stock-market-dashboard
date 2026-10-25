"""
Stock Market Data Fetcher Module.
Uses Requests API as the primary robust engine for real-time quotes, intraday & historical
timeseries bars, and multi-stock comparisons, enriched with fundamentals and news.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import requests
import streamlit as st
import yfinance as yf

# Default headers for Requests API calls to mimic a legitimate browser request
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# Popular presets for quick selection
POPULAR_TICKERS = {
    "Technology": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"],
    "Indices & ETFs": ["SPY", "QQQ", "DIA", "IWM", "VTI"],
    "Semiconductors": ["NVDA", "AMD", "TSM", "AVGO", "INTC", "QCOM"],
    "Finance": ["JPM", "BAC", "GS", "MS", "V", "MA"],
    "Crypto (USD)": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"],
}


def fetch_live_quote_via_requests(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Directly query the Yahoo Finance v8 chart API endpoint using Python Requests.
    Returns real-time price, previous close, high, low, volume, 52-week extremes, etc.
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.strip().upper()}?range=1d&interval=1m"
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=8)
        if response.status_code == 200:
            data = response.json()
            chart_data = data.get("chart", {}).get("result")
            if chart_data and len(chart_data) > 0:
                meta = chart_data[0].get("meta", {})
                current_price = meta.get("regularMarketPrice")
                prev_close = meta.get("chartPreviousClose") or meta.get("previousClose")

                change = None
                change_pct = None
                if current_price is not None and prev_close is not None and prev_close > 0:
                    change = current_price - prev_close
                    change_pct = (change / prev_close) * 100.0

                return {
                    "symbol": symbol.upper(),
                    "short_name": meta.get("shortName", symbol.upper()),
                    "long_name": meta.get("longName", meta.get("shortName", symbol.upper())),
                    "currency": meta.get("currency", "USD"),
                    "exchange": meta.get("exchangeName", "N/A"),
                    "current_price": current_price,
                    "previous_close": prev_close,
                    "change": change,
                    "change_percent": change_pct,
                    "day_high": meta.get("regularMarketDayHigh"),
                    "day_low": meta.get("regularMarketDayLow"),
                    "volume": meta.get("regularMarketVolume"),
                    "fifty_two_week_high": meta.get("fiftyTwoWeekHigh"),
                    "fifty_two_week_low": meta.get("fiftyTwoWeekLow"),
                    "timestamp": meta.get("regularMarketTime"),
                    "source": "Requests API (Direct)",
                }
    except Exception:
        pass
    return None


def fetch_chart_candles_via_requests(
    symbol: str, range_val: str = "1mo", interval: str = "1d"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Directly queries Yahoo Finance v8 chart API via Requests to retrieve
    clean OHLCV timeseries candles and meta information.
    """
    sym = symbol.strip().upper()
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={range_val}&interval={interval}"
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            result = data.get("chart", {}).get("result")
            if result and len(result) > 0:
                item = result[0]
                meta = item.get("meta", {})
                timestamps = item.get("timestamp", [])
                indicators = item.get("indicators", {}).get("quote", [{}])[0]

                if timestamps and "close" in indicators:
                    df = pd.DataFrame({
                        "Datetime": pd.to_datetime(timestamps, unit="s"),
                        "Open": indicators.get("open", []),
                        "High": indicators.get("high", []),
                        "Low": indicators.get("low", []),
                        "Close": indicators.get("close", []),
                        "Volume": indicators.get("volume", []),
                    })
                    # Drop any rows where Close price is missing
                    df.dropna(subset=["Close"], inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    return df, meta
    except Exception:
        pass
    return pd.DataFrame(), {}


@st.cache_data(ttl=20, show_spinner=False)
def get_stock_data(
    symbol: str, period: str = "1mo", interval: str = "1d"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Fetches historical price data and metadata for a given symbol.
    Uses Requests API as primary reliable source for candles & quotes,
    with yfinance enrichment for deeper fundamentals.
    """
    symbol = symbol.strip().upper()
    meta_info: Dict[str, Any] = {}

    # 1. Fetch candles and meta using direct Requests API
    df, meta = fetch_chart_candles_via_requests(symbol, range_val=period, interval=interval)

    # 2. Extract meta values
    if meta:
        current_price = meta.get("regularMarketPrice")
        prev_close = meta.get("chartPreviousClose") or meta.get("previousClose")
        change = None
        change_pct = None
        if current_price is not None and prev_close is not None and prev_close > 0:
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100.0

        meta_info.update({
            "symbol": symbol,
            "short_name": meta.get("shortName", symbol),
            "long_name": meta.get("longName", meta.get("shortName", symbol)),
            "currency": meta.get("currency", "USD"),
            "exchange": meta.get("exchangeName", "N/A"),
            "current_price": current_price,
            "previous_close": prev_close,
            "change": change,
            "change_percent": change_pct,
            "day_high": meta.get("regularMarketDayHigh"),
            "day_low": meta.get("regularMarketDayLow"),
            "volume": meta.get("regularMarketVolume"),
            "fifty_two_week_high": meta.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": meta.get("fiftyTwoWeekLow"),
            "source": "Requests API (Direct v8)",
        })

    # Fallback to yfinance if df is empty
    if df.empty:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            if not df.empty:
                df.reset_index(inplace=True)
                if "Date" in df.columns:
                    df.rename(columns={"Date": "Datetime"}, inplace=True)
                df["Datetime"] = pd.to_datetime(df["Datetime"])
        except Exception:
            pass

    # Ensure current price exists from df if not in meta
    if not meta_info.get("current_price") and not df.empty:
        last_close = df["Close"].iloc[-1]
        meta_info["current_price"] = last_close
        if len(df) > 1:
            p_close = df["Close"].iloc[-2]
            meta_info["previous_close"] = p_close
            meta_info["change"] = last_close - p_close
            meta_info["change_percent"] = ((last_close - p_close) / p_close) * 100.0

    # 3. Enrich with yfinance company metrics
    try:
        ticker = yf.Ticker(symbol)
        yf_info = ticker.info or {}
        meta_info["sector"] = yf_info.get("sector", "N/A")
        meta_info["industry"] = yf_info.get("industry", "N/A")
        meta_info["summary"] = yf_info.get("longBusinessSummary", "No company summary available.")
        meta_info["market_cap"] = yf_info.get("marketCap")
        meta_info["pe_ratio"] = yf_info.get("trailingPE")
        meta_info["forward_pe"] = yf_info.get("forwardPE")
        meta_info["peg_ratio"] = yf_info.get("pegRatio")
        meta_info["eps"] = yf_info.get("trailingEps")
        meta_info["beta"] = yf_info.get("beta")
        meta_info["dividend_yield"] = (
            yf_info.get("dividendYield", 0) * 100 if yf_info.get("dividendYield") else 0.0
        )
        meta_info["target_mean_price"] = yf_info.get("targetMeanPrice")
        meta_info["profit_margins"] = (
            yf_info.get("profitMargins", 0) * 100 if yf_info.get("profitMargins") else 0.0
        )
        meta_info["recommendation"] = yf_info.get("recommendationKey", "N/A").replace("_", " ").title()
    except Exception:
        # Defaults if fundamental data lookup is not available
        meta_info.setdefault("summary", "Company fundamentals unavailable.")

    return df, meta_info


@st.cache_data(ttl=60, show_spinner=False)
def get_multiple_stocks_comparison(symbols: List[str], period: str = "1mo") -> pd.DataFrame:
    """
    Downloads historical close prices for multiple tickers via Requests API and normalizes
    them to percentage return (base 0%) for comparative benchmark analysis.
    """
    combined_df = pd.DataFrame()
    for s in symbols:
        sym = s.strip().upper()
        if not sym:
            continue
        try:
            hist, _ = fetch_chart_candles_via_requests(sym, range_val=period, interval="1d")
            if not hist.empty and len(hist) > 1:
                hist["Date"] = pd.to_datetime(hist["Datetime"]).dt.date
                first_close = hist["Close"].iloc[0]
                hist[sym] = ((hist["Close"] - first_close) / first_close) * 100.0

                if combined_df.empty:
                    combined_df = hist[["Date", sym]].copy()
                else:
                    combined_df = pd.merge(combined_df, hist[["Date", sym]], on="Date", how="outer")
        except Exception:
            continue

    if not combined_df.empty:
        combined_df.sort_values(by="Date", inplace=True)
        combined_df.ffill(inplace=True)
        combined_df.dropna(inplace=True)
    return combined_df


@st.cache_data(ttl=300, show_spinner=False)
def get_company_news(symbol: str) -> List[Dict[str, Any]]:
    """
    Fetches the latest news headlines and summaries for a ticker using Requests API (RSS)
    with fallback to yfinance.
    """
    articles: List[Dict[str, Any]] = []
    sym = symbol.strip().upper()

    # 1. Direct Requests API RSS feed
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={sym}&region=US&lang=en-US"
    try:
        import xml.etree.ElementTree as ET
        response = requests.get(rss_url, headers=DEFAULT_HEADERS, timeout=8)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall(".//item")
            for item in items[:10]:
                title_elem = item.find("title")
                link_elem = item.find("link")
                pub_elem = item.find("pubDate")
                
                title = title_elem.text if title_elem is not None else ""
                link = link_elem.text if link_elem is not None else "#"
                time_str = pub_elem.text if pub_elem is not None else ""

                if title:
                    articles.append({
                        "title": title,
                        "publisher": "Yahoo Finance / Media Partner",
                        "link": link,
                        "time": time_str,
                    })
    except Exception:
        pass

    # 2. Fallback to yfinance if RSS returned nothing
    if not articles:
        try:
            ticker = yf.Ticker(sym)
            news_items = ticker.news or []
            for item in news_items[:8]:
                title = item.get("title")
                publisher = item.get("publisher", "Unknown")
                link = item.get("link", "#")
                pub_time = item.get("providerPublishTime")
                time_str = ""
                if pub_time:
                    dt = datetime.fromtimestamp(pub_time, tz=timezone.utc)
                    time_str = dt.strftime("%Y-%m-%d %H:%M UTC")

                if title:
                    articles.append({
                        "title": title,
                        "publisher": publisher,
                        "link": link,
                        "time": time_str,
                    })
        except Exception:
            pass

    return articles
