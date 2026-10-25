"""
Technical and Financial Indicators Calculation Module using Pandas and NumPy.
Calculates SMA, EMA, RSI, MACD, Bollinger Bands, ATR, VWAP, Stochastic Oscillator,
returns, volatility, and aggregated technical signals.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


def compute_sma(df: pd.DataFrame, window: int = 20, price_col: str = "Close") -> pd.Series:
    """Calculates Simple Moving Average."""
    return df[price_col].rolling(window=window, min_periods=1).mean()


def compute_ema(df: pd.DataFrame, span: int = 20, price_col: str = "Close") -> pd.Series:
    """Calculates Exponential Moving Average."""
    return df[price_col].ewm(span=span, adjust=False).mean()


def compute_rsi(df: pd.DataFrame, window: int = 14, price_col: str = "Close") -> pd.Series:
    """
    Calculates Relative Strength Index (RSI) using Wilder's Smoothing.
    """
    delta = df[price_col].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's smoothing via ewm (alpha = 1 / window)
    avg_gain = gain.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def compute_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    price_col: str = "Close",
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculates MACD Line, Signal Line, and MACD Histogram.
    """
    ema_fast = df[price_col].ewm(span=fast, adjust=False).mean()
    ema_slow = df[price_col].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_bollinger_bands(
    df: pd.DataFrame, window: int = 20, num_std: float = 2.0, price_col: str = "Close"
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Calculates Middle Band (SMA), Upper Band, Lower Band, Bandwidth, and %B.
    """
    middle = df[price_col].rolling(window=window, min_periods=1).mean()
    std = df[price_col].rolling(window=window, min_periods=1).std()
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    bandwidth = (upper - lower) / (middle + 1e-10)
    percent_b = (df[price_col] - lower) / (upper - lower + 1e-10)
    return upper, middle, lower, bandwidth, percent_b


def compute_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Calculates Average True Range (ATR).
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()
    return atr


def compute_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Calculates Volume Weighted Average Price (VWAP).
    Typical Price = (High + Low + Close) / 3
    """
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
    vol = df["Volume"]
    cum_pv = (typical_price * vol).cumsum()
    cum_vol = vol.cumsum()
    vwap = cum_pv / (cum_vol + 1e-10)
    return vwap


def compute_stochastic_oscillator(
    df: pd.DataFrame, k_period: int = 14, d_period: int = 3
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculates Fast %K and Slow %D Stochastic Oscillator.
    """
    lowest_low = df["Low"].rolling(window=k_period, min_periods=1).min()
    highest_high = df["High"].rolling(window=k_period, min_periods=1).max()
    
    k_line = 100.0 * ((df["Close"] - lowest_low) / (highest_high - lowest_low + 1e-10))
    d_line = k_line.rolling(window=d_period, min_periods=1).mean()
    return k_line, d_line


def compute_obv(df: pd.DataFrame) -> pd.Series:
    """
    Calculates On-Balance Volume (OBV).
    """
    direction = np.sign(df["Close"].diff()).fillna(0)
    obv = (direction * df["Volume"]).cumsum()
    return obv


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches the input DataFrame with all technical indicators.
    Returns a copy of the dataframe with added indicator columns.
    """
    if df.empty or len(df) < 2:
        return df

    data = df.copy()

    # Moving Averages
    data["SMA_20"] = compute_sma(data, 20)
    data["SMA_50"] = compute_sma(data, 50)
    data["SMA_200"] = compute_sma(data, 200)
    data["EMA_12"] = compute_ema(data, 12)
    data["EMA_26"] = compute_ema(data, 26)
    data["EMA_50"] = compute_ema(data, 50)

    # Bollinger Bands
    upper, mid, lower, bw, pct_b = compute_bollinger_bands(data, 20, 2.0)
    data["BB_Upper"] = upper
    data["BB_Middle"] = mid
    data["BB_Lower"] = lower
    data["BB_Bandwidth"] = bw
    data["BB_PctB"] = pct_b

    # RSI
    data["RSI_14"] = compute_rsi(data, 14)

    # MACD
    macd, sig, hist = compute_macd(data, 12, 26, 9)
    data["MACD"] = macd
    data["MACD_Signal"] = sig
    data["MACD_Hist"] = hist

    # Stochastic Oscillator
    stoch_k, stoch_d = compute_stochastic_oscillator(data, 14, 3)
    data["Stoch_K"] = stoch_k
    data["Stoch_D"] = stoch_d

    # ATR
    if "High" in data.columns and "Low" in data.columns:
        data["ATR_14"] = compute_atr(data, 14)

    # VWAP & OBV
    if "Volume" in data.columns:
        data["VWAP"] = compute_vwap(data)
        data["OBV"] = compute_obv(data)
        data["Volume_SMA20"] = data["Volume"].rolling(window=20, min_periods=1).mean()

    # Returns & Volatility
    data["Daily_Return"] = data["Close"].pct_change()
    data["Cumulative_Return"] = (1.0 + data["Daily_Return"].fillna(0)).cumprod() - 1.0

    return data


def generate_technical_signals(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyzes the latest values of indicators to generate a consolidated
    bullish / bearish / neutral technical assessment and score.
    """
    if df.empty or len(df) < 5:
        return {
            "overall_score": 0,
            "overall_signal": "Neutral",
            "signals": [],
            "bullish_count": 0,
            "bearish_count": 0,
            "neutral_count": 0,
        }

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    signals = []
    bullish = 0
    bearish = 0
    neutral = 0

    current_price = latest["Close"]

    # 1. RSI Indicator
    rsi_val = latest.get("RSI_14")
    if pd.notna(rsi_val):
        if rsi_val > 70:
            signals.append({
                "indicator": "RSI (14)",
                "value": f"{rsi_val:.1f}",
                "condition": "Overbought (> 70)",
                "sentiment": "Bearish",
                "badge": "🔴 Sell / Caution",
            })
            bearish += 1
        elif rsi_val < 30:
            signals.append({
                "indicator": "RSI (14)",
                "value": f"{rsi_val:.1f}",
                "condition": "Oversold (< 30)",
                "sentiment": "Bullish",
                "badge": "🟢 Buy Opportunity",
            })
            bullish += 1
        else:
            signals.append({
                "indicator": "RSI (14)",
                "value": f"{rsi_val:.1f}",
                "condition": "Neutral Range (30-70)",
                "sentiment": "Neutral",
                "badge": "⚪ Neutral",
            })
            neutral += 1

    # 2. MACD Crossover
    macd_val = latest.get("MACD")
    macd_sig = latest.get("MACD_Signal")
    if pd.notna(macd_val) and pd.notna(macd_sig):
        if macd_val > macd_sig:
            signals.append({
                "indicator": "MACD",
                "value": f"{macd_val:.2f} > {macd_sig:.2f}",
                "condition": "Bullish Crossover (Above Signal)",
                "sentiment": "Bullish",
                "badge": "🟢 Bullish",
            })
            bullish += 1
        else:
            signals.append({
                "indicator": "MACD",
                "value": f"{macd_val:.2f} < {macd_sig:.2f}",
                "condition": "Bearish Crossover (Below Signal)",
                "sentiment": "Bearish",
                "badge": "🔴 Bearish",
            })
            bearish += 1

    # 3. SMA 20 Trend
    sma_20 = latest.get("SMA_20")
    if pd.notna(sma_20):
        if current_price > sma_20:
            signals.append({
                "indicator": "Price vs SMA 20",
                "value": f"${current_price:.2f} vs ${sma_20:.2f}",
                "condition": "Trading Above Short-Term Trend",
                "sentiment": "Bullish",
                "badge": "🟢 Bullish",
            })
            bullish += 1
        else:
            signals.append({
                "indicator": "Price vs SMA 20",
                "value": f"${current_price:.2f} vs ${sma_20:.2f}",
                "condition": "Trading Below Short-Term Trend",
                "sentiment": "Bearish",
                "badge": "🔴 Bearish",
            })
            bearish += 1

    # 4. SMA 50 vs SMA 200 (Golden / Death Cross Context)
    sma_50 = latest.get("SMA_50")
    sma_200 = latest.get("SMA_200")
    if pd.notna(sma_50) and pd.notna(sma_200):
        if sma_50 > sma_200:
            signals.append({
                "indicator": "SMA 50 vs 200",
                "value": f"${sma_50:.2f} > ${sma_200:.2f}",
                "condition": "Golden Cross Alignment",
                "sentiment": "Bullish",
                "badge": "🟢 Bullish",
            })
            bullish += 1
        else:
            signals.append({
                "indicator": "SMA 50 vs 200",
                "value": f"${sma_50:.2f} < ${sma_200:.2f}",
                "condition": "Death Cross Alignment",
                "sentiment": "Bearish",
                "badge": "🔴 Bearish",
            })
            bearish += 1

    # 5. Bollinger Bands Position
    bb_upper = latest.get("BB_Upper")
    bb_lower = latest.get("BB_Lower")
    if pd.notna(bb_upper) and pd.notna(bb_lower):
        if current_price >= bb_upper:
            signals.append({
                "indicator": "Bollinger Bands",
                "value": f"${current_price:.2f} >= ${bb_upper:.2f}",
                "condition": "Touching / Above Upper Band",
                "sentiment": "Bearish",
                "badge": "🔴 Overextended",
            })
            bearish += 1
        elif current_price <= bb_lower:
            signals.append({
                "indicator": "Bollinger Bands",
                "value": f"${current_price:.2f} <= ${bb_lower:.2f}",
                "condition": "Touching / Below Lower Band",
                "sentiment": "Bullish",
                "badge": "🟢 Oversold Bounce Area",
            })
            bullish += 1
        else:
            signals.append({
                "indicator": "Bollinger Bands",
                "value": "Inside Bands",
                "condition": "Normal Volatility Band",
                "sentiment": "Neutral",
                "badge": "⚪ In Range",
            })
            neutral += 1

    # 6. Stochastic Oscillator
    stoch_k = latest.get("Stoch_K")
    if pd.notna(stoch_k):
        if stoch_k > 80:
            signals.append({
                "indicator": "Stochastic %K",
                "value": f"{stoch_k:.1f}",
                "condition": "Overbought Zone (> 80)",
                "sentiment": "Bearish",
                "badge": "🔴 Overbought",
            })
            bearish += 1
        elif stoch_k < 20:
            signals.append({
                "indicator": "Stochastic %K",
                "value": f"{stoch_k:.1f}",
                "condition": "Oversold Zone (< 20)",
                "sentiment": "Bullish",
                "badge": "🟢 Oversold",
            })
            bullish += 1
        else:
            signals.append({
                "indicator": "Stochastic %K",
                "value": f"{stoch_k:.1f}",
                "condition": "Neutral Range (20-80)",
                "sentiment": "Neutral",
                "badge": "⚪ Neutral",
            })
            neutral += 1

    total_factors = bullish + bearish + neutral
    # Calculate composite score from -100 to +100
    if total_factors > 0:
        score = int(((bullish - bearish) / total_factors) * 100)
    else:
        score = 0

    if score >= 45:
        overall_signal = "Strong Buy"
    elif score >= 15:
        overall_signal = "Buy"
    elif score <= -45:
        overall_signal = "Strong Sell"
    elif score <= -15:
        overall_signal = "Sell"
    else:
        overall_signal = "Neutral"

    return {
        "overall_score": score,
        "overall_signal": overall_signal,
        "signals": signals,
        "bullish_count": bullish,
        "bearish_count": bearish,
        "neutral_count": neutral,
    }

