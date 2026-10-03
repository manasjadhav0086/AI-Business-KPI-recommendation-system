import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
from src.formatter import format_business_number

# Enterprise Color Palette
PRIMARY_COLOR = "#3B82F6"      # Blue
SECONDARY_COLOR = "#10B981"    # Green
ACCENT_COLOR = "#8B5CF6"       # Purple
ALERT_COLOR = "#EF4444"        # Red
WARNING_COLOR = "#F59E0B"      # Amber
GRID_COLOR = "rgba(255, 255, 255, 0.08)"

def apply_enterprise_theme(fig: go.Figure, height: int = 400, title: str = "") -> go.Figure:
    """
    Applies consistent enterprise visual styling to Plotly figures.
    """
    fig.update_layout(
        template="plotly_dark",
        height=height,
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=15, color="#F3F4F6"),
            x=0.01,
            y=0.96
        ),
        margin=dict(l=20, r=20, t=45 if title else 20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color="#D1D5DB", size=12),
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family="Inter, sans-serif"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=GRID_COLOR,
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)"
        )
    )
    return fig

def plot_revenue_trend(
    ts_df: pd.DataFrame,
    show_ma: bool = True,
    currency_symbol: str = "₹",
    numbering_mode: str = "Indian",
    title: str = ""
) -> go.Figure:
    """
    Interactive time-series line chart with formatted tooltips and moving averages.
    """
    fig = go.Figure()

    if ts_df.empty:
        return apply_enterprise_theme(fig, title=title)

    # Actual Revenue Line & Area
    fig.add_trace(go.Scatter(
        x=ts_df["date"],
        y=ts_df["revenue"],
        name="Actual Revenue",
        mode="lines",
        line=dict(color=PRIMARY_COLOR, width=2),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.08)",
        customdata=[format_business_number(v, "currency", currency_symbol, numbering_mode) for v in ts_df["revenue"]],
        hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br><b>Revenue:</b> %{customdata}<extra></extra>"
    ))

    # 7-day Moving Average
    if show_ma and "ma_7" in ts_df.columns:
        fig.add_trace(go.Scatter(
            x=ts_df["date"],
            y=ts_df["ma_7"],
            name="7-Day MA",
            mode="lines",
            line=dict(color=WARNING_COLOR, width=1.8, dash="dash"),
            customdata=[format_business_number(v, "currency", currency_symbol, numbering_mode) for v in ts_df["ma_7"]],
            hovertemplate="<b>7D MA:</b> %{customdata}<extra></extra>"
        ))

    # 30-day Moving Average
    if show_ma and "ma_30" in ts_df.columns:
        fig.add_trace(go.Scatter(
            x=ts_df["date"],
            y=ts_df["ma_30"],
            name="30-Day MA",
            mode="lines",
            line=dict(color=SECONDARY_COLOR, width=2.2),
            customdata=[format_business_number(v, "currency", currency_symbol, numbering_mode) for v in ts_df["ma_30"]],
            hovertemplate="<b>30D MA:</b> %{customdata}<extra></extra>"
        ))

    return apply_enterprise_theme(fig, title=title)

def plot_revenue_waterfall(
    waterfall_items: List[Dict[str, Any]],
    currency_symbol: str = "₹",
    numbering_mode: str = "Indian",
    title: str = ""
) -> go.Figure:
    """
    Waterfall chart for period-over-period variance decomposition.
    """
    fig = go.Figure()

    if not waterfall_items:
        return apply_enterprise_theme(fig, title=title)

    names = [item["name"] for item in waterfall_items]
    values = [item["value"] for item in waterfall_items]
    measure_types = ["absolute" if item["type"] == "total" else "relative" for item in waterfall_items]

    text_labels = [
        format_business_number(v, "currency", currency_symbol, numbering_mode) if t == "total"
        else ("+" if v > 0 else "") + format_business_number(v, "currency", currency_symbol, numbering_mode)
        for v, t in zip(values, [item["type"] for item in waterfall_items])
    ]

    fig.add_trace(go.Waterfall(
        name="Impact",
        orientation="v",
        measure=measure_types,
        x=names,
        textposition="outside",
        text=text_labels,
        y=values,
        connector=dict(line=dict(color="rgba(255,255,255,0.2)")),
        decreasing=dict(marker=dict(color=ALERT_COLOR)),
        increasing=dict(marker=dict(color=SECONDARY_COLOR)),
        totals=dict(marker=dict(color=PRIMARY_COLOR))
    ))

    fig.update_layout(waterfallgap=0.3)
    return apply_enterprise_theme(fig, title=title)

def plot_regional_ranked_bar(
    reg_df: pd.DataFrame,
    top_n: int = 12,
    metric: str = "revenue",
    currency_symbol: str = "₹",
    numbering_mode: str = "Indian",
    title: str = ""
) -> go.Figure:
    """
    Ranked horizontal bar chart for regional distribution.
    """
    fig = go.Figure()

    if reg_df.empty or "region" not in reg_df.columns:
        return apply_enterprise_theme(fig, title=title)

    df_plot = reg_df.head(top_n).sort_values(metric, ascending=True)

    text_labels = [
        f"{format_business_number(v, 'currency', currency_symbol, numbering_mode)} ({s:.1f}%)"
        if metric == "revenue" else f"{format_business_number(v, 'count', currency_symbol, numbering_mode)}"
        for v, s in zip(df_plot[metric], df_plot["share_pct"])
    ]

    fig.add_trace(go.Bar(
        y=df_plot["region"],
        x=df_plot[metric],
        orientation="h",
        marker=dict(
            color=df_plot[metric],
            colorscale="Blues",
            line=dict(color="rgba(255,255,255,0.1)", width=1)
        ),
        text=text_labels,
        textposition="auto",
        customdata=df_plot["share_pct"],
        hovertemplate="<b>Region:</b> %{y}<br><b>Value:</b> %{x:,.2f}<br><b>Share:</b> %{customdata:.1f}%<extra></extra>"
    ))

    return apply_enterprise_theme(fig, title=title)

def plot_product_pareto_chart(
    prod_df: pd.DataFrame,
    top_n: int = 15,
    currency_symbol: str = "₹",
    numbering_mode: str = "Indian",
    title: str = ""
) -> go.Figure:
    """
    Pareto 80/20 category revenue and cumulative share % curve.
    """
    fig = go.Figure()

    if prod_df.empty or "product" not in prod_df.columns:
        return apply_enterprise_theme(fig, title=title)

    df_plot = prod_df.head(top_n)

    # Category Revenue Bar
    fig.add_trace(go.Bar(
        x=df_plot["product"],
        y=df_plot["revenue"],
        name="Category Revenue",
        marker=dict(color=PRIMARY_COLOR),
        customdata=[format_business_number(v, "currency", currency_symbol, numbering_mode) for v in df_plot["revenue"]],
        hovertemplate="<b>%{x}</b><br>Revenue: %{customdata}<extra></extra>"
    ))

    # Cumulative % Line
    fig.add_trace(go.Scatter(
        x=df_plot["product"],
        y=df_plot["cumulative_share_pct"],
        name="Cumulative Share %",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#F97316", width=2.2),
        marker=dict(size=6, color="#F97316"),
        hovertemplate="<b>Cumulative:</b> %{y:.1f}%<extra></extra>"
    ))

    # 80% Cutoff line
    fig.add_hline(y=80, line_dash="dash", line_color=ALERT_COLOR, yref="y2", annotation_text="80% Cutoff", annotation_position="top right")

    fig.update_layout(
        yaxis2=dict(
            title="Cumulative Share %",
            overlaying="y",
            side="right",
            range=[0, 105],
            showgrid=False
        ),
        xaxis=dict(tickangle=-40)
    )

    return apply_enterprise_theme(fig, title=title)

def plot_product_treemap(df: pd.DataFrame, top_n: int = 20, title: str = "") -> go.Figure:
    """
    Hierarchy Treemap for multi-dimensional product & regional distribution.
    """
    if df.empty or "product" not in df.columns:
        return apply_enterprise_theme(go.Figure(), title=title)

    top_prods = df.groupby("product")["revenue"].sum().nlargest(top_n).index
    df_filtered = df[df["product"].isin(top_prods)]
    
    path_cols = ["product", "region"] if "region" in df.columns else ["product"]
    agg = df_filtered.groupby(path_cols).agg(revenue=("revenue", "sum")).reset_index()

    fig = px.treemap(
        agg,
        path=path_cols,
        values="revenue",
        color="revenue",
        color_continuous_scale="Viridis"
    )

    fig.update_traces(
        textinfo="label+value+percent parent",
        hovertemplate="<b>%{label}</b><br>Revenue: ₹%{value:,.2f}<extra></extra>"
    )

    return apply_enterprise_theme(fig, title=title)

def plot_anomaly_timeline(
    daily_df: pd.DataFrame,
    anomalies_df: pd.DataFrame,
    currency_symbol: str = "₹",
    numbering_mode: str = "Indian",
    title: str = ""
) -> go.Figure:
    """
    Time-series timeline with overlaid severity anomaly diamonds.
    """
    fig = go.Figure()

    if daily_df.empty:
        return apply_enterprise_theme(fig, title=title)

    # Daily baseline
    fig.add_trace(go.Scatter(
        x=daily_df["date"],
        y=daily_df["revenue"],
        name="Daily Revenue",
        mode="lines",
        line=dict(color="rgba(156, 163, 175, 0.5)", width=1.5),
        customdata=[format_business_number(v, "currency", currency_symbol, numbering_mode) for v in daily_df["revenue"]],
        hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br>Revenue: %{customdata}<extra></extra>"
    ))

    # Anomaly Markers
    if not anomalies_df.empty:
        color_map = {
            "CRITICAL": "#EF4444",
            "HIGH": "#F97316",
            "MEDIUM": "#FBBF24",
            "LOW": "#60A5FA"
        }

        for sev, color in color_map.items():
            subset = anomalies_df[anomalies_df["severity"] == sev]
            if not subset.empty:
                fig.add_trace(go.Scatter(
                    x=subset["date"],
                    y=subset["revenue"],
                    name=f"Anomaly: {sev}",
                    mode="markers",
                    marker=dict(color=color, size=9, symbol="diamond", line=dict(color="white", width=1)),
                    customdata=[format_business_number(v, "currency", currency_symbol, numbering_mode) for v in subset["revenue"]],
                    hovertemplate=f"<b>Date:</b> %{{x|%Y-%m-%d}}<br><b>Revenue:</b> %{{customdata}}<br><b>Severity:</b> {sev}<extra></extra>"
                ))

    return apply_enterprise_theme(fig, title=title)

def plot_forecast_intervals(
    forecast_df: pd.DataFrame,
    currency_symbol: str = "₹",
    numbering_mode: str = "Indian",
    title: str = ""
) -> go.Figure:
    """
    Prophet forward trajectory with 80% confidence intervals.
    """
    fig = go.Figure()

    if forecast_df.empty:
        return apply_enterprise_theme(fig, title=title)

    # Historical Actuals
    hist = forecast_df[~forecast_df["y"].isna()]
    fig.add_trace(go.Scatter(
        x=hist["ds"],
        y=hist["y"],
        name="Historical Actual",
        mode="lines",
        line=dict(color="rgba(156, 163, 175, 0.8)", width=1.5),
        customdata=[format_business_number(v, "currency", currency_symbol, numbering_mode) for v in hist["y"]],
        hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br>Actual: %{customdata}<extra></extra>"
    ))

    # Confidence Interval Upper
    fig.add_trace(go.Scatter(
        x=forecast_df["ds"],
        y=forecast_df["yhat_upper"],
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False
    ))

    # Confidence Interval Lower
    fig.add_trace(go.Scatter(
        x=forecast_df["ds"],
        y=forecast_df["yhat_lower"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(16, 185, 129, 0.15)",
        name="80% Confidence Interval",
        hoverinfo="skip"
    ))

    # Future Projection
    future = forecast_df[forecast_df["y"].isna()]
    fig.add_trace(go.Scatter(
        x=future["ds"],
        y=future["yhat"],
        name="Forecast (yhat)",
        mode="lines",
        line=dict(color=SECONDARY_COLOR, width=2.5),
        customdata=[format_business_number(v, "currency", currency_symbol, numbering_mode) for v in future["yhat"]],
        hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br>Forecast: %{customdata}<extra></extra>"
    ))

    return apply_enterprise_theme(fig, title=title)
