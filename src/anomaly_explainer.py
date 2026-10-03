import pandas as pd
from typing import List, Dict, Any

def explain_anomaly(df: pd.DataFrame, anomalies: pd.DataFrame) -> List[str]:
    """
    Generates structured AI-driven explanations and root-cause drivers
    for each detected anomaly date.
    """
    if df.empty or anomalies.empty:
        return []

    explanations = []
    df_clean = df.copy()
    df_clean["date_only"] = pd.to_datetime(df_clean["date"]).dt.normalize()

    for _, row in anomalies.iterrows():
        anomaly_date = pd.to_datetime(row["date"]).normalize()
        date_str = anomaly_date.strftime("%Y-%m-%d")
        revenue_val = float(row["revenue"])
        expected_val = float(row.get("expected", row.get("mean", 0.0)))
        dev_pct = float(row.get("deviation_pct", 0.0))
        severity = str(row.get("severity", "MEDIUM"))
        anomaly_type = str(row.get("type", "Spike"))

        day_data = df_clean[df_clean["date_only"] == anomaly_date]

        if not day_data.empty:
            region_group = day_data.groupby("region")["revenue"].sum().sort_values(ascending=False)
            top_region = region_group.index[0]
            top_region_rev = float(region_group.iloc[0])
            top_region_share = (top_region_rev / revenue_val * 100) if revenue_val > 0 else 0.0

            product_group = day_data.groupby("product")["revenue"].sum().sort_values(ascending=False)
            top_product = product_group.index[0]
            top_product_rev = float(product_group.iloc[0])
            top_product_share = (top_product_rev / revenue_val * 100) if revenue_val > 0 else 0.0

            orders_count = len(day_data)
        else:
            top_region = "Unknown"
            top_region_share = 0.0
            top_product = "Unknown"
            top_product_share = 0.0
            orders_count = 0

        action_phrase = "surge in order volume" if anomaly_type == "Spike" else "sharp contraction in activity"

        explanation = f"""
[ANOMALY] Detected on {date_str} [{severity} {anomaly_type.upper()}]
- Actual Revenue: Rs. {revenue_val:,.2f} vs Expected: Rs. {expected_val:,.2f} ({dev_pct:+.1f}% deviation).
- Key Driver Product: '{top_product}' contributed Rs. {top_product_rev:,.2f} ({top_product_share:.1f}% of daily revenue).
- Key Driver Region: '{top_region}' generated Rs. {top_region_rev:,.2f} ({top_region_share:.1f}% of daily revenue).
- Operational Context: Recorded {orders_count} orders reflecting a {action_phrase}.
""".strip()

        explanations.append(explanation)

    return explanations