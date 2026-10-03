import pandas as pd
from typing import Dict, Any, List

def calculate_business_health_scorecard(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes deterministic Business Health metrics across 5 operational pillars.
    Statuses are strictly calculated using explicit mathematical rules.
    """
    if df.empty:
        return {"overall_score": 0, "pillars": []}

    total_revenue = float(df["revenue"].sum())
    total_orders = len(df)
    median_aov = float(df["revenue"].median())
    current_aov = float(df["revenue"].mean()) if total_orders > 0 else 0.0

    # 1. Growth Momentum (MoM)
    monthly = df.groupby("month")["revenue"].sum().reset_index().sort_values("month")
    growth_mom = 0.0
    if len(monthly) >= 2:
        curr_m = monthly.iloc[-1]["revenue"]
        prev_m = monthly.iloc[-2]["revenue"]
        growth_mom = ((curr_m - prev_m) / prev_m * 100) if prev_m > 0 else 0.0

    if growth_mom >= 0.0:
        growth_status = "HEALTHY"
        growth_badge = "🟢 Healthy"
        growth_score = 95
        growth_diag = f"MoM revenue growth is positive (+{growth_mom:.1f}%)."
    elif growth_mom >= -10.0:
        growth_status = "MODERATE"
        growth_badge = "🟡 Moderate"
        growth_score = 70
        growth_diag = f"Slight MoM contraction observed ({growth_mom:.1f}%)."
    else:
        growth_status = "AT_RISK"
        growth_badge = "🔴 Needs Attention"
        growth_score = 45
        growth_diag = f"Significant MoM decline detected ({growth_mom:.1f}%)."

    # 2. Revenue Stability (Anomaly Frequency)
    daily = df.groupby("date_only")["revenue"].sum().reset_index()
    total_days = max(len(daily), 1)
    mean_d = daily["revenue"].mean()
    std_d = daily["revenue"].std() if len(daily) > 1 else 1.0
    zscores = (daily["revenue"] - mean_d) / (std_d if std_d > 0 else 1.0)
    anomaly_days = (zscores.abs() > 2.0).sum()
    anomaly_rate = (anomaly_days / total_days * 100)

    if anomaly_rate <= 3.0:
        stability_status = "HEALTHY"
        stability_badge = "🟢 Healthy"
        stability_score = 95
        stability_diag = f"High revenue stability with low anomaly rate ({anomaly_rate:.1f}%)."
    elif anomaly_rate <= 7.0:
        stability_status = "MODERATE"
        stability_badge = "🟡 Moderate"
        stability_score = 70
        stability_diag = f"Moderate revenue volatility detected ({anomaly_rate:.1f}% anomaly days)."
    else:
        stability_status = "AT_RISK"
        stability_badge = "🔴 Needs Attention"
        stability_score = 45
        stability_diag = f"Elevated revenue volatility ({anomaly_rate:.1f}% anomaly days)."

    # 3. Product Concentration Risk
    prod_shares = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    top_5_prod_share = (prod_shares.head(5).sum() / total_revenue * 100) if total_revenue > 0 else 0.0

    if top_5_prod_share <= 35.0:
        prod_status = "HEALTHY"
        prod_badge = "🟢 Healthy"
        prod_score = 95
        prod_diag = f"Well diversified catalog; Top 5 categories represent {top_5_prod_share:.1f}% of sales."
    elif top_5_prod_share <= 55.0:
        prod_status = "MODERATE"
        prod_badge = "🟡 Moderate"
        prod_score = 75
        prod_diag = f"Moderate category concentration; Top 5 categories account for {top_5_prod_share:.1f}% of sales."
    else:
        prod_status = "AT_RISK"
        prod_badge = "🔴 Needs Attention"
        prod_score = 50
        prod_diag = f"High concentration risk; Top 5 categories generate {top_5_prod_share:.1f}% of revenue."

    # 4. Regional Breadth
    reg_shares = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    top_reg_name = reg_shares.index[0] if not reg_shares.empty else "N/A"
    top_reg_share = (reg_shares.iloc[0] / total_revenue * 100) if not reg_shares.empty and total_revenue > 0 else 0.0

    if top_reg_share <= 30.0:
        reg_status = "HEALTHY"
        reg_badge = "🟢 Healthy"
        reg_score = 95
        reg_diag = f"Balanced regional distribution; leading region ({top_reg_name}) holds {top_reg_share:.1f}% share."
    elif top_reg_share <= 50.0:
        reg_status = "MODERATE"
        reg_badge = "🟡 Moderate"
        reg_score = 75
        reg_diag = f"Moderate regional concentration in {top_reg_name} ({top_reg_share:.1f}% share)."
    else:
        reg_status = "AT_RISK"
        reg_badge = "🔴 Needs Attention"
        reg_score = 50
        reg_diag = f"High regional dependency; {top_reg_name} contributes {top_reg_share:.1f}% of total sales."

    # 5. Ticket Size (AOV) Health
    aov_ratio = (current_aov / median_aov) if median_aov > 0 else 1.0
    if aov_ratio >= 1.0:
        aov_status = "HEALTHY"
        aov_badge = "🟢 Healthy"
        aov_score = 90
        aov_diag = f"Average Order Value (₹{current_aov:,.1f}) outperforms historical median (₹{median_aov:,.1f})."
    elif aov_ratio >= 0.85:
        aov_status = "MODERATE"
        aov_badge = "🟡 Moderate"
        aov_score = 70
        aov_diag = f"AOV is slightly below historical median (₹{current_aov:,.1f} vs ₹{median_aov:,.1f})."
    else:
        aov_status = "AT_RISK"
        aov_badge = "🔴 Needs Attention"
        aov_score = 50
        aov_diag = f"AOV shows noticeable dilution (₹{current_aov:,.1f} vs ₹{median_aov:,.1f})."

    # Overall Composite Score (0-100)
    overall_score = round((growth_score + stability_score + prod_score + reg_score + aov_score) / 5)

    pillars = [
        {
            "name": "Growth Momentum",
            "metric": f"{growth_mom:+.1f}% MoM",
            "status": growth_status,
            "badge": growth_badge,
            "score": growth_score,
            "diagnostic": growth_diag,
            "rule": "Healthy if MoM growth ≥ 0%; Moderate if between -10% and 0%; At Risk if < -10%."
        },
        {
            "name": "Revenue Stability",
            "metric": f"{anomaly_rate:.1f}% Anomaly Rate",
            "status": stability_status,
            "badge": stability_badge,
            "score": stability_score,
            "diagnostic": stability_diag,
            "rule": "Healthy if anomaly rate ≤ 3%; Moderate if between 3% and 7%; At Risk if > 7%."
        },
        {
            "name": "Product Diversification",
            "metric": f"{top_5_prod_share:.1f}% Top 5 Share",
            "status": prod_status,
            "badge": prod_badge,
            "score": prod_score,
            "diagnostic": prod_diag,
            "rule": "Healthy if Top 5 categories ≤ 35% of total revenue; Moderate if 35-55%; At Risk if > 55%."
        },
        {
            "name": "Regional Balance",
            "metric": f"{top_reg_share:.1f}% ({top_reg_name})",
            "status": reg_status,
            "badge": reg_badge,
            "score": reg_score,
            "diagnostic": reg_diag,
            "rule": "Healthy if top region ≤ 30% of sales; Moderate if 30-50%; At Risk if > 50%."
        },
        {
            "name": "Ticket Size (AOV)",
            "metric": f"₹{current_aov:,.1f} Mean AOV",
            "status": aov_status,
            "badge": aov_badge,
            "score": aov_score,
            "diagnostic": aov_diag,
            "rule": "Healthy if Mean AOV ≥ Median AOV; Moderate if 85-100%; At Risk if < 85%."
        }
    ]

    return {
        "overall_score": overall_score,
        "pillars": pillars
    }
