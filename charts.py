"""
Plotly Chart Builder Module.
Creates interactive TradingView-style financial charts, multi-subplot technical analysis,
normalized stock comparisons, and gauge widgets.
"""

from typing import List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Dark financial theme palette
THEME = {
    "bg_color": "#0E1117",
    "paper_color": "#0E1117",
    "grid_color": "#1E222D",
    "text_color": "#D1D4DC",
    "bull_color": "#089981",  # Crisp financial green
    "bear_color": "#F23645",  # Crisp financial red
    "sma20_color": "#2962FF",
    "sma50_color": "#FF9800",
    "sma200_color": "#E040FB",
    "ema12_color": "#00BCD4",
    "ema26_color": "#FF5722",
    "bb_color": "rgba(41, 98, 255, 0.2)",
    "vwap_color": "#FFD700",
}


def build_stock_chart(
    df: pd.DataFrame,
    symbol: str,
    chart_type: str = "Candlestick",
    show_volume: bool = True,
    show_sma: bool = True,
    show_ema: bool = False,
    show_bb: bool = True,
    show_vwap: bool = False,
    show_rsi: bool = True,
    show_macd: bool = True,
    show_stoch: bool = False,
) -> go.Figure:
    """
    Constructs a professional multi-panel Plotly financial chart with customizable
    overlays and indicator subplots.
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No chart data available",
            showarrow=False,
            font=dict(size=20, color=THEME["text_color"]),
        )
        return fig

    # Determine required subplots and their row heights
    rows = 1
    row_heights = [0.55]
    specs = [[{"secondary_y": False}]]

    # Secondary indicator rows
    ind_count = sum([show_volume, show_rsi, show_macd, show_stoch])
    
    if show_volume:
        rows += 1
        row_heights.append(0.15)
        specs.append([{"secondary_y": False}])

    if show_rsi:
        rows += 1
        row_heights.append(0.15)
        specs.append([{"secondary_y": False}])

    if show_macd:
        rows += 1
        row_heights.append(0.15)
        specs.append([{"secondary_y": False}])

    if show_stoch:
        rows += 1
        row_heights.append(0.15)
        specs.append([{"secondary_y": False}])

    # Normalize row heights to sum to 1.0
    total_height = sum(row_heights)
    row_heights = [h / total_height for h in row_heights]

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        specs=specs,
    )

    x_axis = df["Datetime"]

    # 1. Main Price Series (Row 1)
    if chart_type == "Candlestick":
        fig.add_trace(
            go.Candlestick(
                x=x_axis,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name=f"{symbol} Price",
                increasing_line_color=THEME["bull_color"],
                decreasing_line_color=THEME["bear_color"],
                showlegend=False,
            ),
            row=1,
            col=1,
        )
    elif chart_type == "OHLC":
        fig.add_trace(
            go.Ohlc(
                x=x_axis,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name=f"{symbol} OHLC",
                increasing_line_color=THEME["bull_color"],
                decreasing_line_color=THEME["bear_color"],
                showlegend=False,
            ),
            row=1,
            col=1,
        )
    elif chart_type == "Area":
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["Close"],
                mode="lines",
                name=f"{symbol} Close",
                line=dict(color="#2962FF", width=2),
                fill="tozeroy",
                fillcolor="rgba(41, 98, 255, 0.15)",
            ),
            row=1,
            col=1,
        )
    else:  # Line Chart
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["Close"],
                mode="lines",
                name=f"{symbol} Close",
                line=dict(color="#2962FF", width=2),
            ),
            row=1,
            col=1,
        )

    # Overlays on Main Chart
    if show_sma:
        if "SMA_20" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x_axis,
                    y=df["SMA_20"],
                    mode="lines",
                    name="SMA 20",
                    line=dict(color=THEME["sma20_color"], width=1.3),
                ),
                row=1,
                col=1,
            )
        if "SMA_50" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x_axis,
                    y=df["SMA_50"],
                    mode="lines",
                    name="SMA 50",
                    line=dict(color=THEME["sma50_color"], width=1.3),
                ),
                row=1,
                col=1,
            )
        if "SMA_200" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x_axis,
                    y=df["SMA_200"],
                    mode="lines",
                    name="SMA 200",
                    line=dict(color=THEME["sma200_color"], width=1.5),
                ),
                row=1,
                col=1,
            )

    if show_ema:
        if "EMA_12" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x_axis,
                    y=df["EMA_12"],
                    mode="lines",
                    name="EMA 12",
                    line=dict(color=THEME["ema12_color"], width=1.2, dash="dot"),
                ),
                row=1,
                col=1,
            )
        if "EMA_26" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x_axis,
                    y=df["EMA_26"],
                    mode="lines",
                    name="EMA 26",
                    line=dict(color=THEME["ema26_color"], width=1.2, dash="dot"),
                ),
                row=1,
                col=1,
            )

    if show_bb and "BB_Upper" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["BB_Upper"],
                mode="lines",
                name="BB Upper",
                line=dict(color="rgba(150, 150, 150, 0.5)", width=1),
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["BB_Lower"],
                mode="lines",
                name="BB Lower",
                line=dict(color="rgba(150, 150, 150, 0.5)", width=1),
                fill="tonexty",
                fillcolor=THEME["bb_color"],
                showlegend=False,
            ),
            row=1,
            col=1,
        )

    if show_vwap and "VWAP" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["VWAP"],
                mode="lines",
                name="VWAP",
                line=dict(color=THEME["vwap_color"], width=1.5, dash="dash"),
            ),
            row=1,
            col=1,
        )

    current_row = 2

    # 2. Volume Subplot
    if show_volume and "Volume" in df.columns:
        vol_colors = [
            THEME["bull_color"] if c >= o else THEME["bear_color"]
            for c, o in zip(df["Close"], df["Open"])
        ]
        fig.add_trace(
            go.Bar(
                x=x_axis,
                y=df["Volume"],
                marker_color=vol_colors,
                name="Volume",
                opacity=0.8,
            ),
            row=current_row,
            col=1,
        )
        if "Volume_SMA20" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=x_axis,
                    y=df["Volume_SMA20"],
                    mode="lines",
                    name="Vol SMA20",
                    line=dict(color="#FF9800", width=1),
                ),
                row=current_row,
                col=1,
            )
        fig.update_yaxes(title_text="Vol", row=current_row, col=1)
        current_row += 1

    # 3. RSI Subplot
    if show_rsi and "RSI_14" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["RSI_14"],
                mode="lines",
                name="RSI (14)",
                line=dict(color="#E040FB", width=1.5),
            ),
            row=current_row,
            col=1,
        )
        # Upper (70) and Lower (30) reference bounds
        fig.add_hline(
            y=70, line_dash="dash", line_color=THEME["bear_color"], opacity=0.7, row=current_row, col=1
        )
        fig.add_hline(
            y=30, line_dash="dash", line_color=THEME["bull_color"], opacity=0.7, row=current_row, col=1
        )
        fig.update_yaxes(
            title_text="RSI",
            range=[0, 100],
            tickvals=[30, 50, 70],
            row=current_row,
            col=1,
        )
        current_row += 1

    # 4. MACD Subplot
    if show_macd and "MACD" in df.columns:
        hist_colors = [
            THEME["bull_color"] if val >= 0 else THEME["bear_color"]
            for val in df["MACD_Hist"].fillna(0)
        ]
        fig.add_trace(
            go.Bar(
                x=x_axis,
                y=df["MACD_Hist"],
                marker_color=hist_colors,
                name="MACD Hist",
                opacity=0.7,
            ),
            row=current_row,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["MACD"],
                mode="lines",
                name="MACD",
                line=dict(color="#2962FF", width=1.3),
            ),
            row=current_row,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["MACD_Signal"],
                mode="lines",
                name="Signal",
                line=dict(color="#FF9800", width=1.2),
            ),
            row=current_row,
            col=1,
        )
        fig.add_hline(y=0, line_color="gray", line_width=0.8, row=current_row, col=1)
        fig.update_yaxes(title_text="MACD", row=current_row, col=1)
        current_row += 1

    # 5. Stochastic Oscillator Subplot
    if show_stoch and "Stoch_K" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["Stoch_K"],
                mode="lines",
                name="%K",
                line=dict(color="#00E676", width=1.3),
            ),
            row=current_row,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df["Stoch_D"],
                mode="lines",
                name="%D",
                line=dict(color="#FF5252", width=1.2, dash="dot"),
            ),
            row=current_row,
            col=1,
        )
        fig.add_hline(y=80, line_dash="dash", line_color="#FF5252", opacity=0.7, row=current_row, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="#00E676", opacity=0.7, row=current_row, col=1)
        fig.update_yaxes(
            title_text="Stoch",
            range=[0, 100],
            tickvals=[20, 50, 80],
            row=current_row,
            col=1,
        )
        current_row += 1

    # Layout styling
    calc_height = max(550, 380 + (ind_count * 120))
    fig.update_layout(
        template="plotly_dark",
        height=calc_height,
        margin=dict(l=40, r=40, t=30, b=40),
        paper_bgcolor=THEME["paper_color"],
        plot_bgcolor=THEME["bg_color"],
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        xaxis=dict(
            rangeslider=dict(visible=False),
            showgrid=True,
            gridcolor=THEME["grid_color"],
        ),
    )

    fig.update_yaxes(showgrid=True, gridcolor=THEME["grid_color"])
    return fig


def build_comparison_chart(df_comp: pd.DataFrame) -> go.Figure:
    """
    Renders comparative performance lines (% Return) for multiple tickers.
    """
    fig = go.Figure()
    if df_comp.empty or "Date" not in df_comp.columns:
        fig.add_annotation(
            text="No comparative data found.",
            showarrow=False,
            font=dict(size=16, color=THEME["text_color"]),
        )
        return fig

    symbols = [col for col in df_comp.columns if col != "Date"]
    palette = ["#2962FF", "#00E676", "#FF9800", "#E040FB", "#00BCD4", "#FF5252"]

    for idx, sym in enumerate(symbols):
        color = palette[idx % len(palette)]
        fig.add_trace(
            go.Scatter(
                x=df_comp["Date"],
                y=df_comp[sym],
                mode="lines",
                name=sym,
                line=dict(color=color, width=2),
                hovertemplate=f"<b>{sym}</b>: %{{y:.2f}}%<extra></extra>",
            )
        )

    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255, 255, 255, 0.4)")

    fig.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=40, r=40, t=30, b=40),
        paper_bgcolor=THEME["paper_color"],
        plot_bgcolor=THEME["bg_color"],
        hovermode="x unified",
        yaxis=dict(
            title="Percentage Return (%)",
            ticksuffix="%",
            gridcolor=THEME["grid_color"],
        ),
        xaxis=dict(gridcolor=THEME["grid_color"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    )
    return fig


def build_range_gauge(current: float, low: float, high: float, title: str = "52-Week Range") -> go.Figure:
    """
    Creates a visual horizontal gauge chart displaying where the current price sits
    within a range (e.g., 52-week or Day High/Low).
    """
    if not (low and high and high > low and current):
        fig = go.Figure()
        return fig

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=current,
            title={"text": title, "font": {"size": 14, "color": THEME["text_color"]}},
            number={"prefix": "$", "font": {"size": 22, "color": THEME["text_color"]}},
            gauge={
                "axis": {
                    "range": [low, high],
                    "tickformat": "$.2f",
                    "tickcolor": THEME["text_color"],
                },
                "bar": {"color": "#2962FF", "thickness": 0.25},
                "bgcolor": "#1E222D",
                "steps": [
                    {"range": [low, low + (high - low) * 0.33], "color": "rgba(242, 54, 69, 0.2)"},
                    {
                        "range": [low + (high - low) * 0.33, low + (high - low) * 0.66],
                        "color": "rgba(255, 152, 0, 0.2)",
                    },
                    {"range": [low + (high - low) * 0.66, high], "color": "rgba(8, 153, 129, 0.2)"},
                ],
                "threshold": {
                    "line": {"color": "#00E676", "width": 4},
                    "thickness": 0.75,
                    "value": current,
                },
            },
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=180,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor=THEME["paper_color"],
    )
    return fig


def build_signal_gauge(score: int, signal: str) -> go.Figure:
    """
    Builds a speedometer style gauge from -100 (Strong Sell) to +100 (Strong Buy).
    """
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={
                "text": f"Technical Consensus: <b>{signal}</b>",
                "font": {"size": 15, "color": THEME["text_color"]},
            },
            number={"font": {"size": 24, "color": THEME["text_color"]}},
            gauge={
                "axis": {
                    "range": [-100, 100],
                    "tickvals": [-80, -40, 0, 40, 80],
                    "ticktext": ["Strong Sell", "Sell", "Neutral", "Buy", "Strong Buy"],
                    "tickfont": {"size": 10},
                },
                "bar": {"color": "#E040FB", "thickness": 0.3},
                "steps": [
                    {"range": [-100, -40], "color": "rgba(242, 54, 69, 0.4)"},
                    {"range": [-40, 40], "color": "rgba(128, 128, 128, 0.3)"},
                    {"range": [40, 100], "color": "rgba(8, 153, 129, 0.4)"},
                ],
                "threshold": {
                    "line": {"color": "#FFFFFF", "width": 4},
                    "thickness": 0.8,
                    "value": score,
                },
            },
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=200,
        margin=dict(l=20, r=20, t=35, b=20),
        paper_bgcolor=THEME["paper_color"],
    )
    return fig

