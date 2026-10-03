import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

def get_regional_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes comprehensive regional performance statistics.
    """
    if df.empty:
        return pd.DataFrame(columns=["region", "revenue", "share_pct", "orders", "aov", "rank"])

    total_revenue = df["revenue"].sum()
    grouped = (
        df.groupby("region")
        .agg(
            revenue=("revenue", "sum"),
            orders=("revenue", "count"),
            aov=("revenue", "mean")
        )
        .reset_index()
    )

    grouped["share_pct"] = (grouped["revenue"] / total_revenue * 100) if total_revenue > 0 else 0.0
    grouped = grouped.sort_values("revenue", ascending=False).reset_index(drop=True)
    grouped["rank"] = grouped.index + 1
    grouped["cumulative_share_pct"] = grouped["share_pct"].cumsum()
    return grouped

def get_product_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes product category performance, rank, share %, and average ticket size.
    """
    if df.empty:
        return pd.DataFrame(columns=["product", "revenue", "share_pct", "orders", "aov", "rank"])

    total_revenue = df["revenue"].sum()
    grouped = (
        df.groupby("product")
        .agg(
            revenue=("revenue", "sum"),
            orders=("revenue", "count"),
            aov=("revenue", "mean"),
            min_price=("revenue", "min"),
            max_price=("revenue", "max")
        )
        .reset_index()
    )

    grouped["share_pct"] = (grouped["revenue"] / total_revenue * 100) if total_revenue > 0 else 0.0
    grouped = grouped.sort_values("revenue", ascending=False).reset_index(drop=True)
    grouped["rank"] = grouped.index + 1
    grouped["cumulative_share_pct"] = grouped["share_pct"].cumsum()
    grouped["pareto_class"] = np.where(grouped["cumulative_share_pct"] <= 80.0, "Core Driver (Top 80%)", "Long Tail (Remaining 20%)")
    return grouped

def get_pareto_summary(product_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates Pareto 80/20 summary metrics.
    """
    if product_df.empty:
        return {
            "total_categories": 0,
            "core_80_count": 0,
            "core_80_pct": 0.0,
            "top_category": "N/A",
            "top_category_share": 0.0,
            "top_5_share": 0.0
        }

    total_categories = len(product_df)
    core_80 = product_df[product_df["cumulative_share_pct"] <= 80.0]
    core_80_count = len(core_80)
    core_80_pct = (core_80_count / total_categories * 100) if total_categories > 0 else 0.0

    top_cat = product_df.iloc[0]["product"]
    top_cat_share = float(product_df.iloc[0]["share_pct"])
    top_5_share = float(product_df.head(5)["share_pct"].sum())

    return {
        "total_categories": total_categories,
        "core_80_count": core_80_count,
        "core_80_pct": core_80_pct,
        "top_category": top_cat,
        "top_category_share": top_cat_share,
        "top_5_share": top_5_share
    }

def get_time_series_trends(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """
    Generates time-series aggregated metrics with 7-day and 30-day moving averages.
    """
    if df.empty:
        return pd.DataFrame()

    df_ts = df.copy()
    if freq == "D":
        ts = df_ts.groupby("date_only").agg(
            revenue=("revenue", "sum"),
            orders=("revenue", "count"),
            aov=("revenue", "mean")
        ).reset_index().rename(columns={"date_only": "date"})
        ts["ma_7"] = ts["revenue"].rolling(window=7, min_periods=1).mean()
        ts["ma_30"] = ts["revenue"].rolling(window=30, min_periods=1).mean()
    elif freq == "W":
        df_ts["week"] = df_ts["date"].dt.to_period("W").apply(lambda r: r.start_time)
        ts = df_ts.groupby("week").agg(
            revenue=("revenue", "sum"),
            orders=("revenue", "count"),
            aov=("revenue", "mean")
        ).reset_index().rename(columns={"week": "date"})
        ts["ma_4"] = ts["revenue"].rolling(window=4, min_periods=1).mean()
    elif freq == "M":
        df_ts["month_start"] = df_ts["date"].dt.to_period("M").apply(lambda r: r.start_time)
        ts = df_ts.groupby("month_start").agg(
            revenue=("revenue", "sum"),
            orders=("revenue", "count"),
            aov=("revenue", "mean")
        ).reset_index().rename(columns={"month_start": "date"})
        ts["ma_3"] = ts["revenue"].rolling(window=3, min_periods=1).mean()
        ts["mom_growth_pct"] = ts["revenue"].pct_change() * 100

    return ts

def get_day_of_week_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates revenue and order volume by Day of Week.
    """
    if df.empty:
        return pd.DataFrame()

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = (
        df.groupby("day_name")
        .agg(
            revenue=("revenue", "sum"),
            orders=("revenue", "count"),
            avg_order_value=("revenue", "mean")
        )
        .reindex(days_order)
        .reset_index()
        .rename(columns={"day_name": "day_of_week"})
    )
    dow["share_pct"] = (dow["revenue"] / dow["revenue"].sum() * 100) if dow["revenue"].sum() > 0 else 0.0
    return dow

def get_seasonality_heatmap_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a Day-of-Week vs Month heatmap matrix of average daily revenue.
    """
    if df.empty:
        return pd.DataFrame()

    df_clean = df.copy()
    df_clean["month_label"] = df_clean["date"].dt.strftime("%b %Y")
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    pivot = df_clean.pivot_table(
        index="day_name",
        columns="month",
        values="revenue",
        aggfunc="sum",
        fill_value=0.0
    )
    pivot = pivot.reindex(days_order)
    return pivot
