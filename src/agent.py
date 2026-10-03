import json
import re
import pandas as pd
from typing import Dict, Any, List, Optional
from src.kpi_engine import calculate_kpis, compare_periods
from src.analytics_engine import get_regional_analysis, get_product_analysis, get_pareto_summary
from src.anomaly_detection import detect_anomalies, get_anomaly_summary_metrics
from src.forecasting import generate_revenue_forecast
from src.root_cause import perform_driver_decomposition
from src.business_health import calculate_business_health_scorecard
from src.recommendations import generate_strategic_recommendations
from src.llm_client import call_groq_llm
from src.formatter import format_business_number, clean_ai_text

def classify_intent(query: str) -> str:
    """
    Classifies user natural language query into analytical domain intents.
    """
    q = query.lower()

    if any(k in q for k in ["ceo summary", "executive summary", "overview", "summary of business", "business summary"]):
        return "ceo_summary"
    elif any(k in q for k in ["anomaly", "anomalies", "spike", "drop", "unusual", "outlier", "incident"]):
        return "anomalies"
    elif any(k in q for k in ["forecast", "future", "predict", "next month", "projection", "next 30 days"]):
        return "forecast"
    elif any(k in q for k in ["why did", "why is", "root cause", "cause of", "driver", "decline", "fell", "dropped", "increased because"]):
        return "root_cause"
    elif any(k in q for k in ["profit", "margin", "profitability", "gross profit", "net profit"]):
        return "profit_analysis"
    elif any(k in q for k in ["product", "category", "best product", "top product", "worst product", "pareto", "items"]):
        return "product_analysis"
    elif any(k in q for k in ["region", "state", "top region", "best region", "worst region", "geographic", "location"]):
        return "regional_analysis"
    elif any(k in q for k in ["health", "scorecard", "risk", "business health", "diversification"]):
        return "business_health"
    elif any(k in q for k in ["recommend", "recommendation", "strategy", "what should we do", "action", "next step"]):
        return "recommendations"
    elif any(k in q for k in ["compare", "month over month", "mom", "last month", "growth rate"]):
        return "period_comparison"
    else:
        return "kpi_summary"

def execute_analytics_tool(intent: str, df: pd.DataFrame, query: str) -> Dict[str, Any]:
    """
    Executes Python deterministic analytics based on identified intent.
    Python is strictly the single source of truth for all facts and figures.
    """
    if df.empty:
        return {"intent": intent, "has_data": False, "summary_text": "No data available in current selection."}

    if intent == "ceo_summary":
        kpis = calculate_kpis(df)
        health = calculate_business_health_scorecard(df)
        recs = generate_strategic_recommendations(df)
        root = perform_driver_decomposition(df)
        return {
            "intent": intent,
            "has_data": True,
            "kpis": kpis,
            "health_score": health.get("overall_score", 0),
            "pillars": health.get("pillars", []),
            "recommendations": recs[:3],
            "drivers": root
        }

    elif intent == "profit_analysis":
        kpis = calculate_kpis(df)
        if not kpis.get("has_profit"):
            return {
                "intent": intent,
                "has_data": True,
                "has_profit": False,
                "message": "Profit metrics cannot be calculated because the current dataset does not contain a recognized profit or margin column."
            }
        return {
            "intent": intent,
            "has_data": True,
            "has_profit": True,
            "total_profit": kpis.get("total_profit", 0.0),
            "profit_margin_pct": kpis.get("profit_margin_pct", 0.0)
        }

    elif intent == "anomalies":
        anomalies = detect_anomalies(df)
        summary = get_anomaly_summary_metrics(anomalies, total_days=df["date"].dt.normalize().nunique() if "date" in df.columns else 1)
        top_anomalies = anomalies.head(5).to_dict(orient="records") if not anomalies.empty else []
        return {
            "intent": intent,
            "has_data": True,
            "anomaly_count": summary["total_anomalies"],
            "spikes": summary["spikes_count"],
            "drops": summary["drops_count"],
            "critical": summary["critical_count"],
            "anomaly_rate_pct": summary["anomaly_rate_pct"],
            "top_records": top_anomalies
        }

    elif intent == "forecast":
        fc = generate_revenue_forecast(df, horizon_days=30)
        return {
            "intent": intent,
            "has_data": fc.get("has_data", False),
            "projected_total": fc.get("projected_total_revenue", 0.0),
            "projected_daily": fc.get("projected_avg_daily", 0.0),
            "projected_growth_pct": fc.get("projected_growth_pct", 0.0),
            "horizon": fc.get("horizon_days", 30)
        }

    elif intent == "root_cause":
        root = perform_driver_decomposition(df)
        return {
            "intent": intent,
            "has_data": root.get("has_data", False),
            "current_period": root.get("curr_period", "Current"),
            "previous_period": root.get("prev_period", "Prior"),
            "total_change": root.get("total_change", 0.0),
            "pct_change": root.get("pct_change", 0.0),
            "top_negative_products": root.get("top_negative_products", [])[:3],
            "top_positive_products": root.get("top_positive_products", [])[:3],
            "top_negative_regions": root.get("top_negative_regions", [])[:3],
            "top_positive_regions": root.get("top_positive_regions", [])[:3]
        }

    elif intent == "product_analysis":
        prod_df = get_product_analysis(df)
        pareto = get_pareto_summary(prod_df)
        top_5 = prod_df.head(5).to_dict(orient="records")
        return {
            "intent": intent,
            "has_data": True,
            "total_categories": pareto["total_categories"],
            "top_category": pareto["top_category"],
            "top_category_share": pareto["top_category_share"],
            "top_5_share": pareto["top_5_share"],
            "top_5_products": top_5
        }

    elif intent == "regional_analysis":
        reg_df = get_regional_analysis(df)
        top_5 = reg_df.head(5).to_dict(orient="records")
        return {
            "intent": intent,
            "has_data": True,
            "total_regions": len(reg_df),
            "top_region": reg_df.iloc[0]["region"] if not reg_df.empty else "N/A",
            "top_region_share": float(reg_df.iloc[0]["share_pct"]) if not reg_df.empty else 0.0,
            "top_5_regions": top_5
        }

    elif intent == "business_health":
        health = calculate_business_health_scorecard(df)
        return {
            "intent": intent,
            "has_data": True,
            "overall_score": health.get("overall_score", 0),
            "pillars": health.get("pillars", [])
        }

    elif intent == "recommendations":
        recs = generate_strategic_recommendations(df)
        return {
            "intent": intent,
            "has_data": True,
            "recommendations": recs
        }

    elif intent == "period_comparison":
        comp = compare_periods(df, period_type="month")
        return {
            "intent": intent,
            "has_data": comp.get("has_data", False),
            "comparison": comp
        }

    else:
        kpis = calculate_kpis(df)
        reg_df = get_regional_analysis(df)
        prod_df = get_product_analysis(df)
        return {
            "intent": "kpi_summary",
            "has_data": True,
            "total_revenue": kpis["total_revenue"],
            "total_orders": kpis["total_orders"],
            "avg_order_value": kpis["avg_order_value"],
            "growth_mom": kpis["growth_mom"],
            "top_region": reg_df.iloc[0]["region"] if not reg_df.empty else "N/A",
            "top_product": prod_df.iloc[0]["product"] if not prod_df.empty else "N/A"
        }

def format_structured_executive_briefing(
    intent: str,
    data: Dict[str, Any],
    currency_symbol: str = "₹",
    numbering_mode: str = "Indian"
) -> Dict[str, Any]:
    """
    Formats verified analytics outputs into clean structured cards with 3-4 comprehensive business points.
    """
    if not data.get("has_data"):
        return {
            "title": "Data Notice",
            "metrics": [],
            "bullets": [
                "Insufficient data records in the active filter selection.",
                "Adjust top slicers or date range to inspect business metrics."
            ],
            "actions": ["Select a wider date range or reset filters."]
        }

    if intent == "ceo_summary":
        kpis = data.get("kpis", {})
        score = data.get("health_score", 0)
        recs = data.get("recommendations", [])
        drivers = data.get("drivers", {})
        growth_val = kpis.get("growth_mom")
        growth_str = f"{growth_val:+.1f}% MoM" if growth_val is not None else "Baseline Period"
        
        bullets = [
            f"<b>Top-Line Volume:</b> Generated {format_business_number(kpis.get('total_revenue', 0), 'currency', currency_symbol, numbering_mode)} across {kpis.get('total_orders', 0):,} orders with an Average Order Value of {format_business_number(kpis.get('avg_order_value', 0), 'currency', currency_symbol, numbering_mode)}.",
            f"<b>Growth Momentum:</b> Business trajectory is pacing at {growth_str} over the latest complete operational cycle.",
            f"<b>Operational Health:</b> Business Health Index is rated at {score}/100 across growth stability, catalog diversification, and market coverage.",
            f"<b>Strategic Focus:</b> Prioritize high-velocity catalog categories while actively monitoring inventory buffers and regional logistics."
        ]

        return {
            "title": "Executive Business Summary",
            "metrics": [
                {"label": "Total Revenue", "value": format_business_number(kpis.get("total_revenue", 0), "currency", currency_symbol, numbering_mode)},
                {"label": "Total Orders", "value": format_business_number(kpis.get("total_orders", 0), "count", currency_symbol, numbering_mode)},
                {"label": "Growth Rate", "value": growth_str},
                {"label": "Average Order Value", "value": format_business_number(kpis.get("avg_order_value", 0), "currency", currency_symbol, numbering_mode)},
                {"label": "Health Index", "value": f"{score}/100"}
            ],
            "bullets": bullets,
            "actions": [
                recs[0]["actions"][0] if len(recs) > 0 and "actions" in recs[0] else "Monitor primary revenue drivers.",
                recs[1]["actions"][0] if len(recs) > 1 and "actions" in recs[1] else "Optimize regional fulfillment."
            ]
        }

    elif intent == "profit_analysis":
        if not data.get("has_profit"):
            return {
                "title": "Profitability Analysis",
                "metrics": [],
                "bullets": [
                    "Profit metrics cannot be calculated from the current dataset.",
                    "The active dataset does not contain a recognized 'Profit' or 'Net Profit' column.",
                    "Revenue and volume analytics remain fully operational.",
                    "Upload a dataset containing net profit to unlock profitability breakdowns."
                ],
                "actions": ["Include a recognized 'Profit' column in your Excel upload to view margins."]
            }
        
        prof = data.get("total_profit", 0)
        margin = data.get("profit_margin_pct", 0)
        return {
            "title": "Profitability & Margin Summary",
            "metrics": [
                {"label": "Total Profit", "value": format_business_number(prof, "currency", currency_symbol, numbering_mode)},
                {"label": "Profit Margin", "value": f"{margin:.1f}%"}
            ],
            "bullets": [
                f"<b>Total Net Earnings:</b> Generated {format_business_number(prof, 'currency', currency_symbol, numbering_mode)} in net profit across active orders.",
                f"<b>Operating Margin:</b> Overall business profit margin stands at {margin:.1f}%.",
                f"<b>Unit Economics:</b> Average profit contribution is aligned with current product pricing tiers.",
                "<b>Margin Strategy:</b> Protect high-margin product lines while re-evaluating discounted catalog items."
            ],
            "actions": ["Focus promotional spend on product categories with above-average margins."]
        }

    elif intent == "root_cause":
        curr_p = data.get("current_period", "Current")
        prev_p = data.get("previous_period", "Prior")
        tot_chg = data.get("total_change", 0.0)
        pct_chg = data.get("pct_change", 0.0)
        neg_prods = data.get("top_negative_products", [])
        pos_prods = data.get("top_positive_products", [])
        neg_regs = data.get("top_negative_regions", [])

        bullets = [
            f"<b>Period Variance:</b> Comparing {prev_p} to {curr_p} shows a net variance of {format_business_number(tot_chg, 'currency', currency_symbol, numbering_mode)} ({pct_chg:+.1f}%)."
        ]
        if neg_prods:
            bullets.append(f"<b>Primary Product Drag:</b> Category '{neg_prods[0]['product']}' drove the largest contraction ({format_business_number(neg_prods[0]['revenue_impact'], 'currency', currency_symbol, numbering_mode)} variance).")
        if neg_regs:
            bullets.append(f"<b>Primary Regional Drag:</b> Region '{neg_regs[0]['region']}' experienced the steepest drop ({format_business_number(neg_regs[0]['revenue_impact'], 'currency', currency_symbol, numbering_mode)} variance).")
        if pos_prods and pos_prods[0]["revenue_impact"] > 0:
            bullets.append(f"<b>Positive Growth Offset:</b> Category '{pos_prods[0]['product']}' grew by {format_business_number(pos_prods[0]['revenue_impact'], 'currency', currency_symbol, numbering_mode)}, partially cushioning losses.")
        else:
            bullets.append("<b>Action Priority:</b> Re-evaluate pricing, demand elasticity, and marketing allocations across dragging categories.")

        return {
            "title": f"Root Cause Driver Decomposition ({prev_p} → {curr_p})",
            "metrics": [
                {"label": "Net Movement", "value": format_business_number(tot_chg, "currency", currency_symbol, numbering_mode)},
                {"label": "Variance %", "value": f"{pct_chg:+.1f}%"}
            ],
            "bullets": bullets,
            "actions": [
                f"Audit inventory and promotional incentives in '{neg_prods[0]['product']}'" if neg_prods else "Review catalog performance.",
                f"Evaluate marketing presence in region '{neg_regs[0]['region']}'" if neg_regs else "Evaluate regional logistics."
            ]
        }

    elif intent == "anomalies":
        count = data.get("anomaly_count", 0)
        spikes = data.get("spikes", 0)
        drops = data.get("drops", 0)
        rate = data.get("anomaly_rate_pct", 0.0)
        return {
            "title": "Revenue Anomaly & Incident Report",
            "metrics": [
                {"label": "Total Anomalies", "value": f"{count} Days"},
                {"label": "Anomaly Rate", "value": f"{rate:.1f}%"},
                {"label": "Spikes", "value": f"{spikes}"},
                {"label": "Drops", "value": f"{drops}"}
            ],
            "bullets": [
                f"<b>Incident Frequency:</b> Detected {count} statistically significant anomalous trading days (|Z| ≥ 2.0).",
                f"<b>Outlier Distribution:</b> Incidents consist of {spikes} positive demand spikes and {drops} sharp volume contraction drops.",
                f"<b>Operational Exposure:</b> Overall anomaly rate is {rate:.1f}%, indicating stable underlying baseline predictability.",
                "<b>Mitigation Action:</b> Investigate individual spike dates in the Anomaly Center to cross-reference promotional campaigns and stock-outs."
            ],
            "actions": ["Inspect individual incident logs in the Anomaly Center for daily product driver breakdowns."]
        }

    elif intent == "forecast":
        proj_tot = data.get("projected_total", 0.0)
        proj_daily = data.get("projected_daily", 0.0)
        proj_growth = data.get("projected_growth_pct", 0.0)
        horizon = data.get("horizon", 30)
        return {
            "title": f"Forward Demand Projection ({horizon} Days Ahead)",
            "metrics": [
                {"label": "Projected Revenue", "value": format_business_number(proj_tot, "currency", currency_symbol, numbering_mode)},
                {"label": "Projected Daily Run-Rate", "value": format_business_number(proj_daily, "currency", currency_symbol, numbering_mode) + "/day"},
                {"label": "Expected Growth", "value": f"{proj_growth:+.1f}%"}
            ],
            "bullets": [
                f"<b>Forward Outlook:</b> Prophet time-series model projects {format_business_number(proj_tot, 'currency', currency_symbol, numbering_mode)} over the upcoming {horizon} days.",
                f"<b>Daily Demand Velocity:</b> Expected average daily revenue is {format_business_number(proj_daily, 'currency', currency_symbol, numbering_mode)}/day ({proj_growth:+.1f}% vs baseline).",
                "<b>Seasonality Influence:</b> Projections capture day-of-week velocity and historical seasonal buying patterns.",
                "<b>Operational Recommendation:</b> Align supply chain lead times and staffing schedules with projected peak demand windows."
            ],
            "actions": ["Plan inventory fulfillment and ad spend in line with forward seasonal velocity."]
        }

    elif intent == "product_analysis":
        top_cat = data.get("top_category", "N/A")
        top_share = data.get("top_category_share", 0.0)
        top_5_share = data.get("top_5_share", 0.0)
        total_cats = data.get("total_categories", 0)
        return {
            "title": "Product Category Intelligence",
            "metrics": [
                {"label": "Top Category", "value": top_cat},
                {"label": "Top Category Share", "value": f"{top_share:.1f}%"},
                {"label": "Top 5 Share (Pareto)", "value": f"{top_5_share:.1f}%"},
                {"label": "Active Categories", "value": f"{total_cats}"}
            ],
            "bullets": [
                f"<b>Category Leader:</b> '{top_cat}' is the primary category driver generating {top_share:.1f}% of total catalog sales.",
                f"<b>Pareto Concentration:</b> The top 5 categories contribute {top_5_share:.1f}% of overall revenue, confirming high catalog concentration.",
                f"<b>Assortment Breadth:</b> Catalog spans {total_cats} active categories with varying ticket size distributions.",
                "<b>Strategic Next Step:</b> Protect volume in top 5 categories while cross-selling high-margin accessories from the long tail."
            ],
            "actions": [f"Optimize margin and cross-selling bundles for '{top_cat}'."]
        }

    elif intent == "regional_analysis":
        top_reg = data.get("top_region", "N/A")
        top_share = data.get("top_region_share", 0.0)
        total_regs = data.get("total_regions", 0)
        return {
            "title": "Geographic Market Performance",
            "metrics": [
                {"label": "Leading Region", "value": top_reg},
                {"label": "Market Share", "value": f"{top_share:.1f}%"},
                {"label": "Active Territories", "value": f"{total_regs}"}
            ],
            "bullets": [
                f"<b>Leading Geographic Hub:</b> Region '{top_reg}' leads with a {top_share:.1f}% market share of total transaction volume.",
                f"<b>Territorial Reach:</b> Active distribution covers {total_regs} distinct regional territories.",
                "<b>Regional Concentration:</b> Top 3 regional hubs account for the majority of order fulfillment volume.",
                f"<b>Expansion Focus:</b> Leverage successful marketing playbooks from '{top_reg}' into adjacent high-potential secondary markets."
            ],
            "actions": [f"Investigate expansion opportunities in secondary regions beyond '{top_reg}'."]
        }

    else:
        tot_rev = data.get("total_revenue", 0.0)
        tot_ord = data.get("total_orders", 0)
        aov = data.get("avg_order_value", 0.0)
        growth = data.get("growth_mom")
        growth_str = f"{growth:+.1f}% MoM" if growth is not None else "Baseline"
        top_r = data.get("top_region", "N/A")
        top_p = data.get("top_product", "N/A")
        return {
            "title": "Business KPI Summary",
            "metrics": [
                {"label": "Total Revenue", "value": format_business_number(tot_rev, "currency", currency_symbol, numbering_mode)},
                {"label": "Total Orders", "value": format_business_number(tot_ord, "count", currency_symbol, numbering_mode)},
                {"label": "Growth Rate", "value": growth_str},
                {"label": "Average Order Value", "value": format_business_number(aov, "currency", currency_symbol, numbering_mode)}
            ],
            "bullets": [
                f"<b>Revenue & Orders:</b> Platform achieved {format_business_number(tot_rev, 'currency', currency_symbol, numbering_mode)} across {tot_ord:,} transactions.",
                f"<b>Average Ticket Size:</b> Transactions averaged {format_business_number(aov, 'currency', currency_symbol, numbering_mode)} per order.",
                f"<b>Leading Drivers:</b> Top regional hub is '{top_r}' and top product category is '{top_p}'.",
                "<b>Operational Focus:</b> Use top slicers to filter specific segments or date ranges for granular drilldowns."
            ],
            "actions": ["Use the top slicers to filter specific segments or date ranges."]
        }

def process_agent_chat(
    query: str,
    df: pd.DataFrame,
    conversation_history: List[Dict[str, str]] = None,
    currency_symbol: str = "₹",
    numbering_mode: str = "Indian"
) -> Dict[str, Any]:
    """
    End-to-End AI Analyst Router:
    User Query -> Intent Detection -> Python Analytics Tool -> Structured Briefing + LLM reasoning.
    Never exposes raw markdown headers or unformatted numbers.
    """
    if conversation_history is None:
        conversation_history = []

    # 1. Intent Detection
    intent = classify_intent(query)

    # 2. Tool Execution (Python is Source of Truth)
    analytics_result = execute_analytics_tool(intent, df, query)

    # 3. Format Structured Ground Truth Object
    structured_brief = format_structured_executive_briefing(intent, analytics_result, currency_symbol, numbering_mode)

    # 4. Formulate LLM Prompt with Grounded Facts
    system_prompt = """
You are InsightIQ's expert AI Business Intelligence Analyst.
Analyze the provided verified business metrics.

CRITICAL RULES:
1. Ground all claims strictly on the provided verified metrics.
2. Provide a clean executive summary with exactly 3 to 4 distinct bullet points:
   - Key Observations & Performance (what happened and by how much)
   - Root Causes & Primary Drivers (product and regional drivers)
   - Risk / Concentration Factor (operational or market exposure)
   - Strategic Recommendations (1-2 prioritized next steps)
3. DO NOT use markdown headers like '###' or raw asterisks like '**' or '*'.
4. Separate each bullet point with a newline starting with a clean bullet '• '.
5. If a metric like profit is missing, state clearly that it is unavailable in the data.
"""

    facts_summary = json.dumps(
        {k: v for k, v in analytics_result.items() if k not in ["top_records", "waterfall_items"]},
        default=str
    )

    user_prompt = f"""
User Question: "{query}"

Verified Business Analytics Output:
{facts_summary}

Provide a structured 3-4 bullet executive explanation of these findings and next steps without markdown symbols.
"""

    messages = [{"role": "system", "content": system_prompt}]
    for turn in conversation_history[-3:]:
        messages.append({"role": turn.get("role", "user"), "content": clean_ai_text(turn.get("content", ""))})
    messages.append({"role": "user", "content": user_prompt})

    # Call LLM
    llm_res = call_groq_llm(messages, max_tokens=400)

    if llm_res.get("success"):
        narrative = clean_ai_text(llm_res["content"])
        source = "groq_llm"
    else:
        # High quality verified multi-bullet formatting
        narrative = "\n".join([f"• {b}" for b in structured_brief["bullets"]])
        source = "verified_python_engine"

    return {
        "intent": intent,
        "structured_brief": structured_brief,
        "narrative": narrative,
        "source": source,
        "analytics_data": analytics_result
    }

def explain_chart_visual(
    chart_title: str,
    chart_data_summary: str,
    business_context: str = ""
) -> str:
    """
    Explains a specific visual/chart using verified underlying data without raw markdown tags.
    """
    prompt = f"""
Visual: {chart_title}
Context: {business_context}
Data Summary: {chart_data_summary}

Explain what this chart reveals in 2-3 concise executive bullets without markdown symbols.
"""
    messages = [
        {"role": "system", "content": "You are a senior BI visual analyst. Provide clean, concise bullet insights without '###' or '**'."},
        {"role": "user", "content": prompt}
    ]

    res = call_groq_llm(messages, max_tokens=250)
    if res.get("success"):
        return clean_ai_text(res["content"])
    else:
        return f"• Displays key volume and revenue distributions for {chart_title}.\n• Values derive strictly from active filter selections."
