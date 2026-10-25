"""
Real-Time Stock Market Dashboard
Built with Streamlit, Plotly, Pandas, and Requests API.
"""

from datetime import datetime
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from charts import (
    build_comparison_chart,
    build_range_gauge,
    build_signal_gauge,
    build_stock_chart,
)
from indicators import add_all_indicators, generate_technical_signals
from stock_api import (
    POPULAR_TICKERS,
    fetch_live_quote_via_requests,
    get_company_news,
    get_multiple_stocks_comparison,
    get_stock_data,
)

# Page configuration
st.set_page_config(
    page_title="Real-Time Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished financial trading dashboard feel
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #161a25;
        border: 1px solid #232733;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .metric-title {
        color: #848e9c;
        font-size: 0.85rem;
        margin-bottom: 4px;
        font-weight: 500;
    }
    .metric-value {
        color: #eaecef;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .metric-delta-pos {
        color: #089981;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .metric-delta-neg {
        color: #f23645;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161a25;
        border-radius: 6px 6px 0 0;
        padding: 8px 16px;
        color: #b2b5be;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2962ff !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_number(num, prefix="$", default="N/A"):
    """Helper to format large financial numbers into B/M/K."""
    if num is None or num == "N/A":
        return default
    try:
        val = float(num)
        if abs(val) >= 1e12:
            return f"{prefix}{val / 1e12:.2f}T"
        elif abs(val) >= 1e9:
            return f"{prefix}{val / 1e9:.2f}B"
        elif abs(val) >= 1e6:
            return f"{prefix}{val / 1e6:.2f}M"
        elif abs(val) >= 1e3:
            return f"{prefix}{val / 1e3:.2f}K"
        else:
            return f"{prefix}{val:.2f}"
    except (ValueError, TypeError):
        return default


# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("⚡ Market Terminal")
    st.markdown("Real-time quotes, technicals & fundamentals.")
    st.markdown("---")

    # Category and Preset Selection
    category = st.selectbox("Market Sector / Asset Class", list(POPULAR_TICKERS.keys()))
    preset_symbols = POPULAR_TICKERS[category]
    selected_preset = st.selectbox("Select Ticker", preset_symbols, index=0)

    # Custom Symbol override
    custom_symbol = st.text_input(
        "Or Enter Custom Ticker (e.g. NVDA, TSLA, BTC-USD)",
        value="",
        help="Type any valid ticker symbol and press Enter.",
    )
    ticker_symbol = custom_symbol.strip().upper() if custom_symbol.strip() else selected_preset

    st.markdown("---")
    st.subheader("⏱️ Timeframe & Chart")

    timeframe_map = {
        "1 Day (1m)": ("1d", "1m"),
        "5 Days (5m)": ("5d", "5m"),
        "1 Month (30m)": ("1mo", "30m"),
        "6 Months (1d)": ("6mo", "1d"),
        "1 Year (1d)": ("1y", "1d"),
        "5 Years (1wk)": ("5y", "1wk"),
        "Max (1mo)": ("max", "1mo"),
    }
    selected_tf_label = st.selectbox("Timeframe (Period / Interval)", list(timeframe_map.keys()), index=4)
    period, interval = timeframe_map[selected_tf_label]

    chart_type = st.radio(
        "Chart Style",
        ["Candlestick", "Line", "Area", "OHLC"],
        horizontal=True,
    )

    st.markdown("---")
    st.subheader("📐 Technical Indicators")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        show_sma = st.checkbox("SMA (20, 50, 200)", value=True)
        show_ema = st.checkbox("EMA (12, 26)", value=False)
        show_bb = st.checkbox("Bollinger Bands", value=True)
        show_vwap = st.checkbox("VWAP", value=False)
    with col_t2:
        show_vol = st.checkbox("Volume Subplot", value=True)
        show_rsi = st.checkbox("RSI (14)", value=True)
        show_macd = st.checkbox("MACD (12, 26, 9)", value=True)
        show_stoch = st.checkbox("Stochastic %K/%D", value=False)

    st.markdown("---")
    st.subheader("🔄 Real-Time Auto-Refresh")
    auto_refresh = st.checkbox("Enable Live Polling", value=False)
    refresh_interval_sec = st.slider(
        "Refresh Interval (seconds)",
        min_value=5,
        max_value=120,
        value=15,
        step=5,
        disabled=not auto_refresh,
    )

    if auto_refresh:
        st_autorefresh(interval=refresh_interval_sec * 1000, key="stock_autorefresh")

    if st.button("🚀 Refresh Quote Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- MAIN DASHBOARD HEADER ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title(f"📊 {ticker_symbol} Live Dashboard")
with col_head2:
    st.markdown(
        f"<div style='text-align: right; color: #848e9c; padding-top: 15px;'>"
        f"Last synced: <b>{datetime.now().strftime('%H:%M:%S')}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

# Fetch Data
with st.spinner(f"Retrieving market data for {ticker_symbol}..."):
    df_raw, info = get_stock_data(ticker_symbol, period=period, interval=interval)

if df_raw.empty:
    st.error(f"⚠️ Could not load data for '{ticker_symbol}'. Please verify the ticker symbol is valid.")
    st.stop()

# Compute technical indicators
df = add_all_indicators(df_raw)
tech_signals = generate_technical_signals(df)

# Current Pricing & Changes
current_price = info.get("current_price") or (df["Close"].iloc[-1] if not df.empty else None)
prev_close = info.get("previous_close")
change = info.get("change")
change_pct = info.get("change_percent")

if (change is None or change_pct is None) and prev_close and current_price:
    change = current_price - prev_close
    change_pct = (change / prev_close) * 100.0

# --- TOP METRIC CARDS ---
delta_sign = "+" if (change is not None and change >= 0) else ""
delta_color = "metric-delta-pos" if (change is not None and change >= 0) else "metric-delta-neg"

mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)

with mcol1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">CURRENT PRICE</div>
            <div class="metric-value">${current_price:,.2f}</div>
            <div class="{delta_color}">{delta_sign}{change:,.2f} ({delta_sign}{change_pct:.2f}%)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with mcol2:
    day_h = info.get("day_high") or (df["High"].max() if "High" in df.columns else None)
    day_l = info.get("day_low") or (df["Low"].min() if "Low" in df.columns else None)
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">DAY RANGE</div>
            <div class="metric-value" style="font-size: 1.15rem;">
                ${day_l:,.2f} - ${day_h:,.2f}
            </div>
            <div style="color: #848e9c; font-size: 0.85rem;">Low - High</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with mcol3:
    w52_h = info.get("fifty_two_week_high")
    w52_l = info.get("fifty_two_week_low")
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">52-WEEK RANGE</div>
            <div class="metric-value" style="font-size: 1.15rem;">
                {format_number(w52_l)} - {format_number(w52_h)}
            </div>
            <div style="color: #848e9c; font-size: 0.85rem;">52W Extremes</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with mcol4:
    vol = info.get("volume") or (df["Volume"].iloc[-1] if "Volume" in df.columns else None)
    mcap = info.get("market_cap")
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">MARKET CAP / VOLUME</div>
            <div class="metric-value" style="font-size: 1.15rem;">{format_number(mcap)}</div>
            <div style="color: #848e9c; font-size: 0.85rem;">Vol: {format_number(vol, prefix='')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with mcol5:
    pe = info.get("pe_ratio")
    beta = info.get("beta")
    pe_str = f"{pe:.2f}" if pe else "N/A"
    beta_str = f"{beta:.2f}" if beta else "N/A"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">VALUATION & RISK</div>
            <div class="metric-value" style="font-size: 1.15rem;">P/E: {pe_str}</div>
            <div style="color: #848e9c; font-size: 0.85rem;">Beta: {beta_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- DASHBOARD TABS ---
tab_chart, tab_signals, tab_compare, tab_financials, tab_news, tab_data = st.tabs([
    "📈 Interactive Chart",
    "🎯 Technical Signals",
    "📊 Multi-Stock Comparison",
    "📋 Fundamentals & Valuation",
    "📰 Latest News",
    "💾 Raw Data & CSV Export",
])

# --- TAB 1: INTERACTIVE CHART ---
with tab_chart:
    st.markdown(f"**{info.get('long_name', ticker_symbol)}** ({info.get('exchange', 'Market')})")
    chart_fig = build_stock_chart(
        df=df,
        symbol=ticker_symbol,
        chart_type=chart_type,
        show_volume=show_vol,
        show_sma=show_sma,
        show_ema=show_ema,
        show_bb=show_bb,
        show_vwap=show_vwap,
        show_rsi=show_rsi,
        show_macd=show_macd,
        show_stoch=show_stoch,
    )
    st.plotly_chart(chart_fig, use_container_width=True)

    # Sub-gauges for 52W range and Day range
    if w52_l and w52_h and current_price:
        gcol1, gcol2 = st.columns([1, 1])
        with gcol1:
            g_52 = build_range_gauge(current_price, w52_l, w52_h, title="52-Week Range Position")
            st.plotly_chart(g_52, use_container_width=True)
        with gcol2:
            if day_l and day_h and day_h > day_l:
                g_day = build_range_gauge(current_price, day_l, day_h, title="Today's Session Range")
                st.plotly_chart(g_day, use_container_width=True)

# --- TAB 2: TECHNICAL SIGNALS ---
with tab_signals:
    st.subheader("🎯 Technical Analysis & Indicator Consensus")
    col_sig1, col_sig2 = st.columns([1, 2])

    with col_sig1:
        speedo = build_signal_gauge(tech_signals["overall_score"], tech_signals["overall_signal"])
        st.plotly_chart(speedo, use_container_width=True)
        
        st.markdown(
            f"""
            - **Bullish Factors:** `{tech_signals['bullish_count']}`
            - **Bearish Factors:** `{tech_signals['bearish_count']}`
            - **Neutral Factors:** `{tech_signals['neutral_count']}`
            """
        )

        # Support & Resistance Calculation (Classic Pivot Points)
        if len(df) > 1 and "High" in df.columns:
            h = df["High"].iloc[-1]
            l = df["Low"].iloc[-1]
            c = df["Close"].iloc[-1]
            pivot = (h + l + c) / 3.0
            r1 = (2 * pivot) - l
            s1 = (2 * pivot) - h
            r2 = pivot + (h - l)
            s2 = pivot - (h - l)

            st.markdown("#### 🛡️ Pivot Support & Resistance")
            st.markdown(
                f"""
                | Level | Price |
                | :--- | :--- |
                | **Resistance 2 (R2)** | `${r2:,.2f}` |
                | **Resistance 1 (R1)** | `${r1:,.2f}` |
                | **Pivot Point (P)** | `${pivot:,.2f}` |
                | **Support 1 (S1)** | `${s1:,.2f}` |
                | **Support 2 (S2)** | `${s2:,.2f}` |
                """
            )

    with col_sig2:
        st.markdown("#### 📋 Indicator Condition Details")
        if tech_signals["signals"]:
            sig_table = []
            for item in tech_signals["signals"]:
                sig_table.append({
                    "Indicator": item["indicator"],
                    "Latest Value": item["value"],
                    "Status": item["condition"],
                    "Signal": item["badge"],
                })
            st.dataframe(sig_table, use_container_width=True, hide_index=True)
        else:
            st.info("Insufficient data points to generate detailed signals.")

# --- TAB 3: MULTI-STOCK COMPARISON ---
with tab_compare:
    st.subheader("📊 Comparative Performance Benchmark")
    st.markdown("Compare percentage growth of selected stocks over the chosen timeframe.")
    
    comp_defaults = ["AAPL", "MSFT", "NVDA", "SPY"]
    if ticker_symbol not in comp_defaults:
        comp_defaults.insert(0, ticker_symbol)
    
    compare_tickers = st.multiselect(
        "Select tickers to benchmark against each other",
        options=list(set(comp_defaults + ["GOOGL", "AMZN", "META", "TSLA", "QQQ", "DIA", "BTC-USD"])),
        default=comp_defaults[:4],
    )

    if compare_tickers:
        with st.spinner("Fetching comparison data..."):
            df_comp = get_multiple_stocks_comparison(compare_tickers, period=period)
        if not df_comp.empty:
            fig_comp = build_comparison_chart(df_comp)
            st.plotly_chart(fig_comp, use_container_width=True)

            # Performance Summary Table
            st.markdown("#### Cumulative Returns Summary")
            perf_summary = []
            for sym in [c for c in df_comp.columns if c != "Date"]:
                ret = df_comp[sym].iloc[-1]
                perf_summary.append({
                    "Ticker": sym,
                    "Total Return (%)": f"{ret:+.2f}%",
                    "Performance": "🟢 Outperforming" if ret > 0 else "🔴 Underperforming",
                })
            st.dataframe(perf_summary, use_container_width=True, hide_index=True)
        else:
            st.warning("Could not calculate comparative returns for selected symbols.")

# --- TAB 4: FUNDAMENTALS & VALUATION ---
with tab_financials:
    st.subheader("📋 Fundamental Metrics & Valuation Summary")
    fcol1, fcol2, fcol3 = st.columns(3)

    with fcol1:
        st.markdown("##### 💵 Valuation Multiples")
        st.markdown(
            f"""
            - **Trailing P/E:** `{info.get('pe_ratio', 'N/A')}`
            - **Forward P/E:** `{info.get('forward_pe', 'N/A')}`
            - **PEG Ratio:** `{info.get('peg_ratio', 'N/A')}`
            - **EPS (TTM):** `${info.get('eps', 'N/A')}`
            - **Market Cap:** `{format_number(info.get('market_cap'))}`
            """
        )

    with fcol2:
        st.markdown("##### 📈 Profitability & Dividends")
        div_y = info.get("dividend_yield")
        div_str = f"{div_y:.2f}%" if div_y else "0.00%"
        profit_m = info.get("profit_margins")
        profit_str = f"{profit_m:.2f}%" if profit_m else "N/A"
        st.markdown(
            f"""
            - **Dividend Yield:** `{div_str}`
            - **Profit Margin:** `{profit_str}`
            - **Beta (Volatility):** `{info.get('beta', 'N/A')}`
            - **Sector:** `{info.get('sector', 'N/A')}`
            - **Industry:** `{info.get('industry', 'N/A')}`
            """
        )

    with fcol3:
        st.markdown("##### 🎯 Wall Street Consensus")
        target_p = info.get("target_mean_price")
        target_str = f"${target_p:,.2f}" if target_p else "N/A"
        upside = ""
        if target_p and current_price and current_price > 0:
            up_pct = ((target_p - current_price) / current_price) * 100.0
            upside = f"({up_pct:+.1f}%)"

        st.markdown(
            f"""
            - **Analyst Recommendation:** `{info.get('recommendation', 'N/A')}`
            - **Mean Target Price:** `{target_str} {upside}`
            - **Currency:** `{info.get('currency', 'USD')}`
            - **Data Feed:** `{info.get('source', 'Hybrid (Requests + yfinance)')}`
            """
        )

    st.markdown("---")
    st.markdown("##### 🏢 Company Profile")
    st.write(info.get("summary", "No company profile description available."))

# --- TAB 5: LATEST NEWS ---
with tab_news:
    st.subheader(f"📰 Latest News & Market Headlines for {ticker_symbol}")
    news_items = get_company_news(ticker_symbol)
    if news_items:
        for item in news_items:
            with st.container():
                st.markdown(f"#### [{item['title']}]({item['link']})")
                st.caption(f"Source: {item['publisher']} | Published: {item['time']}")
                st.markdown("---")
    else:
        st.info(f"No recent news articles found for {ticker_symbol}.")

# --- TAB 6: RAW DATA & CSV EXPORT ---
with tab_data:
    st.subheader("💾 Historical Price & Indicator Data")
    st.markdown("View all OHLCV prices alongside computed moving averages, oscillators, and volatility metrics.")
    
    # Format DataFrame for cleaner viewing
    display_df = df.copy()
    if "Datetime" in display_df.columns:
        display_df["Datetime"] = display_df["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    st.dataframe(display_df, use_container_width=True)

    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Download {ticker_symbol} Technical Data as CSV",
        data=csv_data,
        file_name=f"{ticker_symbol}_stock_technicals_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

