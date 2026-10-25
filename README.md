# 📈 Real-Time Stock Market Dashboard

An interactive, Bloomberg/TradingView-style stock market dashboard built with **Python**, **Streamlit**, **Plotly**, **Pandas**, and **Requests API**. Tracks and visualizes real-time and historical stock market data, advanced technical indicators, comparative performance benchmarks, fundamental valuations, and financial news.

---

## ✨ Features

- **⚡ Live Data Streaming & Polling**:
  - Live quote querying via Python **Requests API** directly from real-time endpoints.
  - Optional auto-refresh polling (every 5s, 15s, 30s, 60s, 120s) with manual instantaneous refresh trigger.
  - Multi-asset support: US Equities, ETFs, Global Indices, and Cryptocurrencies (e.g. `BTC-USD`, `ETH-USD`).
- **📊 Interactive Financial Charts (Plotly)**:
  - Chart styles: Candlestick, Line, Area, and OHLC.
  - Integrated Volume subplot with bull (green) and bear (red) coloring.
  - Overlays: Simple Moving Averages (SMA 20, 50, 200), Exponential Moving Averages (EMA 12, 26), Bollinger Bands with shaded volatility envelopes, and VWAP (Volume-Weighted Average Price).
  - Oscillators: Relative Strength Index (RSI 14) with 70/30 threshold shading, MACD (12, 26, 9) with 4-tier colored momentum histogram, and Stochastic Oscillator (%K, %D).
- **🎯 Technical Signals & Analysis**:
  - Algorithmic consensus scoring meter (-100 to +100) mapping to **Strong Buy**, **Buy**, **Neutral**, **Sell**, and **Strong Sell**.
  - Classic Pivot Point Support and Resistance levels ($S_1, S_2, R_1, R_2$).
  - Breakdown table of each active technical signal condition.
- **📈 Multi-Stock Comparison**:
  - Benchmark performance across multiple stocks normalized to percentage return (0% base).
  - Side-by-side cumulative return analysis.
- **📋 Fundamental & Valuation Analysis**:
  - Valuation multiples: Trailing P/E, Forward P/E, PEG Ratio, EPS (TTM), Market Capitalization.
  - Profitability: Profit Margin, Dividend Yield, Beta (Market Risk).
  - Wall Street consensus: Analyst Recommendation Key, Mean Target Price, and Implied Upside/Downside %.
  - Full company business summary.
- **📰 Real-Time News Feed**:
  - Latest financial headlines, publisher badges, and direct links.
- **💾 CSV Export**:
  - 1-click download of historical price data combined with all computed technical indicator metrics.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit**: Web application framework and reactive UI.
- **Plotly**: GPU-accelerated interactive financial graphs, gauges, and subplots.
- **Pandas & NumPy**: Quantitative indicator mathematics and timeseries data processing.
- **Requests API**: Direct real-time quote retrieval.
- **yfinance**: Multi-timeframe historical candle feeds, fundamentals, and news aggregation.

---

## 🚀 Getting Started

### 1. Clone or Navigate to the Project Directory
```powershell
cd C:\Users\singi\.gemini\antigravity\scratch\stock-dashboard
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Launch the Dashboard
```powershell
python -m streamlit run app.py
```
*(or `streamlit run app.py` if your Python Scripts folder is in your PATH)*
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 📂 Project Architecture

```
stock-dashboard/
├── app.py              # Main Streamlit application and layout
├── stock_api.py        # Requests API & yfinance real-time and historical data fetchers
├── indicators.py       # Technical analysis calculations (SMA, EMA, RSI, MACD, BB, ATR, VWAP)
├── charts.py           # Plotly interactive candlestick and multi-panel charts
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
```

