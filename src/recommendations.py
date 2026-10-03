import pandas as pd
from typing import Dict, Any, List

def generate_strategic_recommendations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generates actionable, fact-grounded strategic recommendations
    across Growth, Product, Regional, and Operational pillars.
    """
    if df.empty:
        return []

    total_revenue = float(df["revenue"].sum())
    total_orders = len(df)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

    # Regional metrics
    reg_shares = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    top_region = reg_shares.index[0] if not reg_shares.empty else "Unknown"
    top_reg_share = (reg_shares.iloc[0] / total_revenue * 100) if not reg_shares.empty and total_revenue > 0 else 0.0

    # Product metrics
    prod_shares = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    top_product = prod_shares.index[0] if not prod_shares.empty else "Unknown"
    top_prod_share = (prod_shares.iloc[0] / total_revenue * 100) if not prod_shares.empty and total_revenue > 0 else 0.0

    # Growth trend
    monthly = df.groupby("month")["revenue"].sum().reset_index().sort_values("month")
    growth_mom = 0.0
    if len(monthly) >= 2:
        curr_m = monthly.iloc[-1]["revenue"]
        prev_m = monthly.iloc[-2]["revenue"]
        growth_mom = ((curr_m - prev_m) / prev_m * 100) if prev_m > 0 else 0.0

    recommendations = []

    # 1. Growth Strategy
    if growth_mom < 0:
        recommendations.append({
            "category": "Growth Acceleration",
            "priority": "HIGH",
            "badge": "🔴 High Priority",
            "kpi": "Month-over-Month Revenue",
            "current_value": f"{growth_mom:.1f}%",
            "why_it_matters": "A contraction in monthly top-line momentum signals either reduced conversion, customer attrition, or seasonal transition.",
            "business_interpretation": f"Revenue contracted by {abs(growth_mom):.1f}% in the latest period. Immediate reactivation campaigns and targeted promotions are required.",
            "risk": "Prolonged contraction can lead to inventory overhang and lower operating margins.",
            "actions": [
                f"Audit top declining categories to detect pricing or stock availability bottlenecks.",
                f"Launch targeted discount incentives in core volume region '{top_region}'.",
                "Introduce bundle promotions to elevate average transaction value above the current ₹{:,.1f} baseline.".format(avg_order_value)
            ]
        })
    else:
        recommendations.append({
            "category": "Growth Acceleration",
            "priority": "MEDIUM",
            "badge": "🟢 Momentum",
            "kpi": "Month-over-Month Revenue",
            "current_value": f"+{growth_mom:.1f}%",
            "why_it_matters": "Positive top-line growth creates capital to expand marketing efficiency and scale customer acquisition.",
            "business_interpretation": f"Revenue grew by +{growth_mom:.1f}% MoM. The business should double down on high-converting channels.",
            "risk": "Capacity constraints or stock-outs during high-demand surges.",
            "actions": [
                f"Allocate incremental marketing budget into top category '{top_product}'.",
                "Expand regional logistics capacity to maintain high delivery fulfillment rates.",
                "Implement automated up-sell recommendations to drive higher basket size."
            ]
        })

    # 2. Product Portfolio Strategy
    recommendations.append({
        "category": "Product Strategy",
        "priority": "MEDIUM",
        "badge": "🟡 Strategic",
        "kpi": "Category Concentration (Pareto)",
        "current_value": f"Top Category: {top_product} ({top_prod_share:.1f}%)",
        "why_it_matters": "High dependence on a single category increases supply chain and consumer taste risk.",
        "business_interpretation": f"'{top_product}' generates {top_prod_share:.1f}% of total catalog revenue (₹{prod_shares.iloc[0]:,.2f}).",
        "risk": "A category-specific demand shock could disproportionately impact top-line profitability.",
        "actions": [
            f"Cross-promote second-tier categories alongside '{top_product}' via bundle discounts.",
            "Review vendor margins on top 5 categories to identify margin expansion opportunities.",
            "Prune bottom 10% non-performing categories to streamline logistics."
        ]
    })

    # 3. Regional Expansion Strategy
    recommendations.append({
        "category": "Regional Expansion",
        "priority": "MEDIUM",
        "badge": "🔵 Expansion",
        "kpi": "Geographic Penetration",
        "current_value": f"Leading Region: {top_region} ({top_reg_share:.1f}%)",
        "why_it_matters": "Over-concentration in 1-2 major metropolitan states leaves untapped regional growth opportunities.",
        "business_interpretation": f"'{top_region}' commands {top_reg_share:.1f}% of orders. Secondary tier states represent under-penetrated upside.",
        "risk": "Localized competition or regional regulatory changes in the core market.",
        "actions": [
            "Test localized promotional ad campaigns in promising mid-tier regions.",
            "Optimize regional shipping carrier partnerships to reduce delivery times in secondary states.",
            "Develop regional product affinity bundles tailored to local purchasing preferences."
        ]
    })

    # 4. Operational & Ticket Size Optimization
    recommendations.append({
        "category": "Operations & AOV",
        "priority": "LOW",
        "badge": "⚪ Optimization",
        "kpi": "Average Order Value (AOV)",
        "current_value": f"₹{avg_order_value:,.2f}",
        "why_it_matters": "Increasing AOV is the most cost-effective lever to grow total revenue without increasing customer acquisition costs.",
        "business_interpretation": f"Current transaction value averages ₹{avg_order_value:,.2f} across {total_orders:,} total orders.",
        "risk": "Price sensitivity if minimum order thresholds are raised too aggressively.",
        "actions": [
            "Set free shipping threshold at 15% above the median order value to encourage add-on items.",
            "Incentivize multi-item purchases with tiered volume discounts.",
            "Analyze order-level item affinities for automated checkout recommendations."
        ]
    })

    return recommendations

def generate_recommendation(change: float, region: str, product: str) -> str:
    """
    Backward-compatible recommendation generator matching legacy signature.
    """
    if change < 0:
        return f"""
Business Recommendation:
1. Investigate declining sales of {product} in the {region} region.
2. Consider running targeted marketing campaigns in this region.
3. Introduce limited-time discounts or promotional offers.
4. Review inventory availability and supply chain for this product.
5. Monitor customer feedback to identify demand issues.
""".strip()
    else:
        return f"""
Business Recommendation:
1. Sales of {product} are improving in {region}.
2. Increase marketing investment in this region.
3. Expand product availability to capitalize on demand.
4. Introduce cross-selling opportunities with related products.
""".strip()
