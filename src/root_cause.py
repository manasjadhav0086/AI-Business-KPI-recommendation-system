import pandas as pd
from typing import Dict, Any, Tuple, List, Optional

def root_cause_analysis(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Identifies the single worst performing region and product category
    between the last two available months (backward compatibility).
    """
    if df.empty:
        return None, None

    months = sorted(df["month"].unique())
    if len(months) < 2:
        return None, None

    curr_m, prev_m = months[-1], months[-2]
    curr_df = df[df["month"] == curr_m]
    prev_df = df[df["month"] == prev_m]

    region_curr = curr_df.groupby("region")["revenue"].sum()
    region_prev = prev_df.groupby("region")["revenue"].sum()
    region_diff = region_curr.subtract(region_prev, fill_value=0.0)
    worst_region = str(region_diff.idxmin()) if not region_diff.empty else None

    prod_curr = curr_df.groupby("product")["revenue"].sum()
    prod_prev = prev_df.groupby("product")["revenue"].sum()
    prod_diff = prod_curr.subtract(prod_prev, fill_value=0.0)
    worst_product = str(prod_diff.idxmin()) if not prod_diff.empty else None

    return worst_region, worst_product

def perform_driver_decomposition(
    df: pd.DataFrame,
    period_type: str = "month",
    curr_period: str = None,
    prev_period: str = None
) -> Dict[str, Any]:
    """
    Performs full mathematical decomposition of KPI movement between two periods.
    Decomposes net revenue change into product category drivers and regional drivers.
    """
    if df.empty:
        return {"has_data": False, "message": "No data available."}

    group_col = "month" if period_type == "month" else ("quarter" if period_type == "quarter" else "year")
    periods = sorted(df[group_col].unique())

    if len(periods) < 2:
        return {
            "has_data": True,
            "can_decompose": False,
            "message": "At least 2 periods are required for driver decomposition."
        }

    # If the last period is a partial sliver (<= 3 days) and we have prior months, use the last 2 complete months
    if curr_period and curr_period in periods:
        c_p = curr_period
        p_p = prev_period if (prev_period in periods and prev_period != c_p) else periods[max(0, periods.index(c_p) - 1)]
    else:
        if len(periods) >= 3 and "date_only" in df.columns and df[df[group_col] == periods[-1]]["date_only"].nunique() <= 3:
            c_p = periods[-2]
            p_p = periods[-3]
        else:
            c_p = periods[-1]
            p_p = periods[-2]

    curr_df = df[df[group_col] == c_p]
    prev_df = df[df[group_col] == p_p]

    curr_rev = float(curr_df["revenue"].sum())
    prev_rev = float(prev_df["revenue"].sum())
    total_change = curr_rev - prev_rev
    pct_change = (total_change / prev_rev * 100) if prev_rev > 0 else 0.0

    # 1. Product Drivers
    prod_curr = curr_df.groupby("product")["revenue"].sum()
    prod_prev = prev_df.groupby("product")["revenue"].sum()
    prod_diff = prod_curr.subtract(prod_prev, fill_value=0.0).reset_index()
    prod_diff.columns = ["product", "revenue_impact"]
    prod_diff["pct_contribution"] = (prod_diff["revenue_impact"] / abs(total_change) * 100) if abs(total_change) > 0 else 0.0
    prod_diff = prod_diff.sort_values("revenue_impact", ascending=False)

    top_positive_products = prod_diff.head(5).to_dict(orient="records")
    top_negative_products = prod_diff.sort_values("revenue_impact", ascending=True).head(5).to_dict(orient="records")

    # 2. Regional Drivers
    reg_curr = curr_df.groupby("region")["revenue"].sum()
    reg_prev = prev_df.groupby("region")["revenue"].sum()
    reg_diff = reg_curr.subtract(reg_prev, fill_value=0.0).reset_index()
    reg_diff.columns = ["region", "revenue_impact"]
    reg_diff["pct_contribution"] = (reg_diff["revenue_impact"] / abs(total_change) * 100) if abs(total_change) > 0 else 0.0
    reg_diff = reg_diff.sort_values("revenue_impact", ascending=False)

    top_positive_regions = reg_diff.head(5).to_dict(orient="records")
    top_negative_regions = reg_diff.sort_values("revenue_impact", ascending=True).head(5).to_dict(orient="records")

    # 3. Build Waterfall Chart Data
    waterfall_items = [
        {"name": f"Base ({p_p})", "value": prev_rev, "type": "total"}
    ]

    # Top negative category impacts
    for item in top_negative_products[:3]:
        waterfall_items.append({
            "name": f"Product: {item['product'][:18]}",
            "value": float(item["revenue_impact"]),
            "type": "relative"
        })

    # Top positive category impacts
    for item in top_positive_products[:3]:
        waterfall_items.append({
            "name": f"Product: {item['product'][:18]}",
            "value": float(item["revenue_impact"]),
            "type": "relative"
        })

    waterfall_items.append({"name": f"Final ({c_p})", "value": curr_rev, "type": "total"})

    return {
        "has_data": True,
        "can_decompose": True,
        "curr_period": c_p,
        "prev_period": p_p,
        "current_revenue": curr_rev,
        "previous_revenue": prev_rev,
        "total_change": total_change,
        "pct_change": pct_change,
        "top_positive_products": top_positive_products,
        "top_negative_products": top_negative_products,
        "top_positive_regions": top_positive_regions,
        "top_negative_regions": top_negative_regions,
        "waterfall_items": waterfall_items,
        "product_diff_df": prod_diff,
        "region_diff_df": reg_diff
    }