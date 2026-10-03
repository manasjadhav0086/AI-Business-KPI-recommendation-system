import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes summary business KPIs dynamically based on available columns.
    Protects against partial trailing month distortions and division by zero.
    """
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_orders": 0,
            "avg_order_value": 0.0,
            "active_regions": 0,
            "active_products": 0,
            "has_profit": False,
            "total_profit": 0.0,
            "profit_margin_pct": 0.0,
            "has_quantity": False,
            "total_quantity": 0.0,
            "region": pd.Series(dtype=float),
            "product": pd.Series(dtype=float),
            "growth_mom": None,
            "prior_revenue": 0.0,
            "revenue_change": 0.0,
            "order_growth_mom": None,
            "aov_growth_mom": None,
        }

    total_revenue = float(df["revenue"].sum())
    total_orders = int(len(df))
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
    active_regions = int(df["region"].nunique()) if "region" in df.columns else 1
    active_products = int(df["product"].nunique()) if "product" in df.columns else 1

    revenue_by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False) if "region" in df.columns else pd.Series(dtype=float)
    revenue_by_product = df.groupby("product")["revenue"].sum().sort_values(ascending=False) if "product" in df.columns else pd.Series(dtype=float)

    # Optional Profit & Margin
    has_profit = "profit" in df.columns and df["profit"].notna().any()
    if has_profit:
        total_profit = float(df["profit"].sum())
        profit_margin_pct = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    else:
        total_profit = None
        profit_margin_pct = None

    # Optional Quantity
    has_quantity = "quantity" in df.columns
    total_quantity = float(df["quantity"].sum()) if has_quantity else float(total_orders)

    # Month-over-Month calculation
    growth_mom = None
    prior_revenue = 0.0
    revenue_change = 0.0
    order_growth_mom = None
    aov_growth_mom = None

    if "month" in df.columns:
        monthly_summary = (
            df.groupby("month")
            .agg(
                revenue=("revenue", "sum"),
                orders=("revenue", "count"),
                aov=("revenue", "mean"),
                days=("date_only", "nunique") if "date_only" in df.columns else ("revenue", "count")
            )
            .reset_index()
            .sort_values("month")
        )

        # If the latest month has fewer than 4 recorded days and previous month had >= 15 days,
        # use the last two complete months for accurate MoM trend comparison
        if len(monthly_summary) >= 3 and monthly_summary.iloc[-1]["days"] <= 3 and monthly_summary.iloc[-2]["days"] >= 15:
            compare_curr = monthly_summary.iloc[-2]
            compare_prev = monthly_summary.iloc[-3]
        elif len(monthly_summary) >= 2:
            compare_curr = monthly_summary.iloc[-1]
            compare_prev = monthly_summary.iloc[-2]
        else:
            compare_curr = None
            compare_prev = None

        if compare_curr is not None and compare_prev is not None:
            prior_revenue = float(compare_prev["revenue"])
            revenue_change = float(compare_curr["revenue"] - compare_prev["revenue"])

            if prior_revenue > 100:  # Avoid division by zero or near-zero base
                growth_mom = float((revenue_change / prior_revenue) * 100)

            if compare_prev["orders"] > 10:
                order_growth_mom = float(((compare_curr["orders"] - compare_prev["orders"]) / compare_prev["orders"]) * 100)

            if compare_prev["aov"] > 0:
                aov_growth_mom = float(((compare_curr["aov"] - compare_prev["aov"]) / compare_prev["aov"]) * 100)
    else:
        monthly_summary = pd.DataFrame()

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
        "active_regions": active_regions,
        "active_products": active_products,
        "has_profit": has_profit,
        "total_profit": total_profit,
        "profit_margin_pct": profit_margin_pct,
        "has_quantity": has_quantity,
        "total_quantity": total_quantity,
        "region": revenue_by_region,
        "product": revenue_by_product,
        "growth_mom": growth_mom,
        "prior_revenue": prior_revenue,
        "revenue_change": revenue_change,
        "order_growth_mom": order_growth_mom,
        "aov_growth_mom": aov_growth_mom,
        "monthly_summary": monthly_summary
    }

def compare_periods(df: pd.DataFrame, period_type: str = "month") -> Dict[str, Any]:
    """
    Compares the latest complete period to the preceding period.
    """
    if df.empty or "date" not in df.columns:
        return {"has_data": False, "message": "No date dimension available for period comparison."}

    df_clean = df.copy()
    group_col = "month" if period_type == "month" else ("quarter" if period_type == "quarter" else "year")
    if group_col not in df_clean.columns:
        return {"has_data": False, "message": f"{period_type.capitalize()} field is not present."}

    periods = sorted(df_clean[group_col].unique())
    if len(periods) < 2:
        return {
            "has_data": True,
            "can_compare": False,
            "current_period": str(periods[-1]) if len(periods) > 0 else "N/A",
            "message": "Only 1 period available in current filter selection."
        }

    # If the last period is a partial sliver (e.g. 1-2 days), step back to the full month
    if len(periods) >= 3 and df_clean[df_clean[group_col] == periods[-1]]["date_only"].nunique() <= 3:
        curr_period = periods[-2]
        prev_period = periods[-3]
    else:
        curr_period = periods[-1]
        prev_period = periods[-2]

    curr_df = df_clean[df_clean[group_col] == curr_period]
    prev_df = df_clean[df_clean[group_col] == prev_period]

    curr_rev = float(curr_df["revenue"].sum())
    prev_rev = float(prev_df["revenue"].sum())
    rev_diff = curr_rev - prev_rev
    rev_pct = (rev_diff / prev_rev * 100) if prev_rev > 0 else None

    curr_ord = int(len(curr_df))
    prev_ord = int(len(prev_df))
    ord_diff = curr_ord - prev_ord
    ord_pct = (ord_diff / prev_ord * 100) if prev_ord > 0 else None

    curr_aov = curr_rev / curr_ord if curr_ord > 0 else 0.0
    prev_aov = prev_rev / prev_ord if prev_ord > 0 else 0.0
    aov_diff = curr_aov - prev_aov
    aov_pct = (aov_diff / prev_aov * 100) if prev_aov > 0 else None

    return {
        "has_data": True,
        "can_compare": True,
        "current_period": str(curr_period),
        "previous_period": str(prev_period),
        "current_revenue": curr_rev,
        "previous_revenue": prev_rev,
        "revenue_change": rev_diff,
        "revenue_growth_pct": rev_pct,
        "current_orders": curr_ord,
        "previous_orders": prev_ord,
        "orders_change": ord_diff,
        "orders_growth_pct": ord_pct,
        "current_aov": curr_aov,
        "previous_aov": prev_aov,
        "aov_change": aov_diff,
        "aov_growth_pct": aov_pct
    }