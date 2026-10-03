import os
import pandas as pd
import numpy as np
from prophet import Prophet
import streamlit as st
from typing import Dict, Any, Tuple
from src.db_connection import get_connection

@st.cache_data(show_spinner=False)
def generate_revenue_forecast(
    df: pd.DataFrame,
    horizon_days: int = 30,
    include_history: bool = True
) -> Dict[str, Any]:
    """
    Fits Facebook Prophet model on daily aggregated revenue and forecasts future periods.
    Cached with @st.cache_data for performance.
    """
    if df.empty:
        return {"has_data": False, "message": "Dataset is empty."}

    # Aggregate daily revenue
    df_clean = df.copy()
    df_clean["date_only"] = pd.to_datetime(df_clean["date"]).dt.normalize()
    daily_rev = (
        df_clean.groupby("date_only")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"date_only": "ds", "revenue": "y"})
        .dropna()
        .sort_values("ds")
    )

    if len(daily_rev) < 14:
        return {
            "has_data": False,
            "message": f"Insufficient historical data ({len(daily_rev)} daily points). At least 14 days required."
        }

    # Constrain horizon
    horizon = min(max(horizon_days, 7), 180)

    try:
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=(len(daily_rev) > 180),
            interval_width=0.80,
            changepoint_prior_scale=0.05,
            uncertainty_samples=100
        )
        model.fit(daily_rev)

        future = model.make_future_dataframe(periods=horizon)
        forecast = model.predict(future)

        # Merge with actuals
        merged = pd.merge(forecast, daily_rev, on="ds", how="left")
        merged["yhat"] = merged["yhat"].clip(lower=0.0)
        merged["yhat_lower"] = merged["yhat_lower"].clip(lower=0.0)
        merged["yhat_upper"] = merged["yhat_upper"].clip(lower=0.0)

        # Extract future-only partition
        future_only = merged[merged["y"].isna()].copy()
        historical_only = merged[~merged["y"].isna()].copy()

        # Key forecast summary metrics
        hist_total_rev = float(daily_rev["y"].sum())
        hist_avg_daily = float(daily_rev["y"].mean())
        
        future_total_rev = float(future_only["yhat"].sum())
        future_avg_daily = float(future_only["yhat"].mean())
        future_lower_sum = float(future_only["yhat_lower"].sum())
        future_upper_sum = float(future_only["yhat_upper"].sum())

        projected_growth_pct = ((future_avg_daily - hist_avg_daily) / hist_avg_daily * 100) if hist_avg_daily > 0 else 0.0

        # Save output CSV
        os.makedirs("outputs", exist_ok=True)
        forecast.to_csv("outputs/forecast_data.csv", index=False)

        # Optional MySQL persistence
        try:
            engine = get_connection()
            forecast.to_sql("revenue_forecast", engine, if_exists="replace", index=False)
        except Exception:
            pass

        return {
            "has_data": True,
            "forecast_df": merged,
            "future_df": future_only,
            "history_df": historical_only,
            "horizon_days": horizon,
            "hist_total_revenue": hist_total_rev,
            "hist_avg_daily": hist_avg_daily,
            "projected_total_revenue": future_total_rev,
            "projected_avg_daily": future_avg_daily,
            "projected_lower_bound": future_lower_sum,
            "projected_upper_bound": future_upper_sum,
            "projected_growth_pct": projected_growth_pct,
            "model": model
        }

    except Exception as e:
        return {
            "has_data": False,
            "message": f"Forecasting calculation encountered an error: {str(e)}"
        }

def revenue_forecast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Backward-compatible wrapper returning the full forecast dataframe.
    """
    res = generate_revenue_forecast(df, horizon_days=30)
    if res.get("has_data"):
        return res["forecast_df"]
    return pd.DataFrame()