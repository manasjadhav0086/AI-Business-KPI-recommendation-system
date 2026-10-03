import os
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, List
from src.db_connection import get_connection

def detect_anomalies(
    df: pd.DataFrame,
    z_threshold: float = 2.0,
    method: str = "zscore"
) -> pd.DataFrame:
    """
    Detects statistical revenue anomalies on daily time-series data.
    Supports configurable Z-score threshold and severity categorization.
    """
    if df.empty:
        return pd.DataFrame()

    df_clean = df.copy()
    df_clean["date_only"] = pd.to_datetime(df_clean["date"]).dt.normalize()

    # Aggregate daily revenue
    daily = (
        df_clean.groupby("date_only")["revenue"]
        .agg(revenue="sum", orders="count")
        .reset_index()
        .rename(columns={"date_only": "date"})
        .sort_values("date")
    )

    if len(daily) < 5:
        return pd.DataFrame()

    mean_val = float(daily["revenue"].mean())
    std_val = float(daily["revenue"].std())

    if std_val == 0:
        return pd.DataFrame()

    daily["mean"] = mean_val
    daily["std"] = std_val
    daily["zscore"] = (daily["revenue"] - mean_val) / std_val
    daily["expected"] = daily["revenue"].rolling(window=14, min_periods=1, center=True).median()
    daily["deviation"] = daily["revenue"] - daily["expected"]
    daily["deviation_pct"] = (daily["deviation"] / daily["expected"] * 100).replace([np.inf, -np.inf], 0.0)

    # Filter anomalies based on threshold
    anomalies = daily[daily["zscore"].abs() >= z_threshold].copy()

    # Classify severity
    def assign_severity(z):
        abs_z = abs(z)
        if abs_z >= 3.0:
            return "CRITICAL"
        elif abs_z >= 2.5:
            return "HIGH"
        elif abs_z >= 2.0:
            return "MEDIUM"
        else:
            return "LOW"

    anomalies["severity"] = anomalies["zscore"].apply(assign_severity)
    anomalies["type"] = np.where(anomalies["zscore"] > 0, "Spike", "Drop")

    # Persist to output CSV
    os.makedirs("outputs", exist_ok=True)
    anomalies.to_csv("outputs/anomaly_data.csv", index=False)

    try:
        engine = get_connection()
        anomalies.to_sql("revenue_anomalies", engine, if_exists="replace", index=False)
    except Exception:
        pass

    return anomalies

def get_anomaly_summary_metrics(anomalies_df: pd.DataFrame, total_days: int) -> Dict[str, Any]:
    """
    Computes summary metrics for detected anomalies.
    """
    if anomalies_df.empty:
        return {
            "total_anomalies": 0,
            "spikes_count": 0,
            "drops_count": 0,
            "critical_count": 0,
            "anomaly_rate_pct": 0.0,
            "max_spike_date": "N/A",
            "max_spike_rev": 0.0
        }

    total_count = len(anomalies_df)
    spikes = len(anomalies_df[anomalies_df["type"] == "Spike"])
    drops = len(anomalies_df[anomalies_df["type"] == "Drop"])
    critical = len(anomalies_df[anomalies_df["severity"] == "CRITICAL"])
    rate = (total_count / total_days * 100) if total_days > 0 else 0.0

    max_spike_row = anomalies_df.sort_values("revenue", ascending=False).iloc[0]
    max_date = str(pd.to_datetime(max_spike_row["date"]).strftime("%Y-%m-%d"))
    max_rev = float(max_spike_row["revenue"])

    return {
        "total_anomalies": total_count,
        "spikes_count": spikes,
        "drops_count": drops,
        "critical_count": critical,
        "anomaly_rate_pct": rate,
        "max_spike_date": max_date,
        "max_spike_rev": max_rev
    }