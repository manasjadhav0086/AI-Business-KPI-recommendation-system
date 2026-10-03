import os
import streamlit as st
import pandas as pd
import numpy as np

# Increase pandas styler max render elements limit
pd.set_option("styler.render.max_elements", 5000000)

# Page Configuration
st.set_page_config(
    page_title="AI Business Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Styling (Power BI / Tableau Style)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Mode Status Banner */
    .mode-banner-demo {
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .mode-banner-custom {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Top Horizontal Slicer Container */
    .top-slicer-container {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px 8px 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    .slicer-header {
        font-size: 12px;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    /* Enterprise Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .hero-title {
        font-size: 22px;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 13px;
        color: #94A3B8;
        font-weight: 400;
        line-height: 1.4;
    }

    /* KPI Metric Cards */
    .kpi-container {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        text-align: left;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.5);
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }
    .kpi-delta-positive {
        color: #10B981;
        font-size: 13px;
        font-weight: 600;
        margin-top: 6px;
    }
    .kpi-delta-negative {
        color: #EF4444;
        font-size: 13px;
        font-weight: 600;
        margin-top: 6px;
    }
    .kpi-delta-neutral {
        color: #64748B;
        font-size: 13px;
        font-weight: 500;
        margin-top: 6px;
    }

    /* Structured AI Briefing Container */
    .ai-brief-card {
        background: #1E293B;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 18px;
    }
    .ai-metric-pill {
        background: #0F172A;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 10px 14px;
        text-align: center;
    }
    .ai-metric-pill-label {
        font-size: 11px;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
    }
    .ai-metric-pill-value {
        font-size: 18px;
        color: #F8FAFC;
        font-weight: 800;
        margin-top: 2px;
    }

    /* Card Panels */
    .pillar-card {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Chat styling */
    .user-bubble {
        background: #2563EB;
        color: white;
        padding: 12px 16px;
        border-radius: 12px 12px 2px 12px;
        margin: 8px 0;
        display: inline-block;
        max-width: 80%;
        float: right;
        clear: both;
    }
    .assistant-bubble {
        background: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #E2E8F0;
        padding: 14px 18px;
        border-radius: 12px 12px 12px 2px;
        margin: 8px 0;
        display: inline-block;
        max-width: 85%;
        float: left;
        clear: both;
    }
</style>
""", unsafe_allow_html=True)

# Imports from modular architecture
from src.data_loader import load_dataset, filter_dataset
from src.excel_processor import (
    inspect_excel_workbook,
    detect_best_data_sheet,
    process_uploaded_business_data
)
from src.formatter import format_business_number, clean_ai_text
from src.kpi_engine import calculate_kpis, compare_periods
from src.analytics_engine import (
    get_regional_analysis,
    get_product_analysis,
    get_pareto_summary,
    get_time_series_trends,
    get_seasonality_heatmap_matrix
)
from src.root_cause import perform_driver_decomposition
from src.forecasting import generate_revenue_forecast
from src.anomaly_detection import detect_anomalies, get_anomaly_summary_metrics
from src.anomaly_explainer import explain_anomaly
from src.business_health import calculate_business_health_scorecard
from src.recommendations import generate_strategic_recommendations
from src.data_quality import calculate_data_quality_report
from src.agent import process_agent_chat, explain_chart_visual
from src.visualization import (
    plot_revenue_trend,
    plot_revenue_waterfall,
    plot_regional_ranked_bar,
    plot_product_pareto_chart,
    plot_product_treemap,
    plot_anomaly_timeline,
    plot_forecast_intervals
)
from src.exports import export_df_to_csv, generate_kpi_summary_report
from src.llm_client import get_groq_api_key, get_groq_model

# ---------------------------------------------------------
# 1. INITIALIZE SESSION STATE
# ---------------------------------------------------------
if "data_source" not in st.session_state:
    st.session_state["data_source"] = "default"  # "default" or "custom"
if "custom_df" not in st.session_state:
    st.session_state["custom_df"] = None
if "custom_filename" not in st.session_state:
    st.session_state["custom_filename"] = ""
if "currency_symbol" not in st.session_state:
    st.session_state["currency_symbol"] = "₹"
if "numbering_mode" not in st.session_state:
    st.session_state["numbering_mode"] = "Indian"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ---------------------------------------------------------
# 2. SIDEBAR NAVIGATION & SELF-SERVICE EXCEL UPLOADER
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px;'>
        <div style='display: flex; align-items: center; gap: 8px;'>
            <span style='font-size: 24px;'>📊</span>
            <div>
                <h3 style='margin: 0; color: #3B82F6; font-size: 17px; font-weight: 800;'>DECISION AI</h3>
                <p style='margin: 0; color: #94A3B8; font-size: 11px; font-weight: 500;'>Self-Service BI Platform</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation View Selection
    navigation_page = st.radio(
        "Navigation",
        [
            "🏠 Executive & Performance",
            "📦 Product & Regional Hub",
            "📈 Forecast & Anomaly Center",
            "🤖 AI Business Analyst (Chat)",
            "🔎 Data Explorer & Quality"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # 📁 SELF-SERVICE EXCEL / CSV FILE UPLOADER
    st.markdown("### 📁 Upload Business Data")
    uploaded_file = st.file_uploader(
        "Upload Excel (.xlsx / .xls) or CSV",
        type=["xlsx", "xls", "csv"],
        help="Upload any transaction, orders, or sales data to automatically generate dynamic BI analytics."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name

        # Sheet selection if workbook contains multiple sheets
        sheet_names = inspect_excel_workbook(file_bytes, file_name)
        if len(sheet_names) > 1:
            best_sheet = detect_best_data_sheet(sheet_names)
            selected_sheet = st.selectbox("Select Sheet", sheet_names, index=sheet_names.index(best_sheet) if best_sheet in sheet_names else 0)
        else:
            selected_sheet = sheet_names[0]

        # Process upload
        with st.spinner("Processing & analyzing dataset..."):
            proc_res = process_uploaded_business_data(file_bytes, file_name, selected_sheet=selected_sheet)

        if proc_res.get("success"):
            st.session_state["data_source"] = "custom"
            st.session_state["custom_df"] = proc_res["df"]
            st.session_state["custom_filename"] = file_name
            st.session_state["currency_symbol"] = proc_res.get("currency_symbol", "₹")
            st.session_state["quality_summary"] = proc_res.get("quality_summary", {})
            st.success(f"✅ Loaded {len(proc_res['df']):,} rows from `{file_name}`")
        else:
            st.error(f"⚠️ {proc_res.get('error')}")

    # Reset Data Button (if custom dataset is active)
    if st.session_state["data_source"] == "custom":
        if st.button("🔄 Reset to Default Dataset", use_container_width=True, type="secondary"):
            st.session_state["data_source"] = "default"
            st.session_state["custom_df"] = None
            st.session_state["custom_filename"] = ""
            st.session_state["currency_symbol"] = "₹"
            st.rerun()

    st.markdown("---")

    # ⚙️ DISPLAY SETTINGS (Currency & Numbering Format)
    st.markdown("### ⚙️ Display Settings")
    currency_choices = ["INR ₹", "USD $", "EUR €", "GBP £", "AED د.إ"]
    curr_map = {"INR ₹": "₹", "USD $": "$", "EUR €": "€", "GBP £": "£", "AED د.إ": "د.إ"}
    
    current_symbol = st.session_state.get("currency_symbol", "₹")
    default_curr_idx = 0
    for idx, (label, sym) in enumerate(curr_map.items()):
        if sym == current_symbol:
            default_curr_idx = idx
            break

    chosen_curr_label = st.selectbox("Currency", currency_choices, index=default_curr_idx)
    st.session_state["currency_symbol"] = curr_map[chosen_curr_label]

    numbering_mode = st.radio("Number Format", ["Indian (Lakh / Crore)", "International (K / M / B)"], index=0 if st.session_state["numbering_mode"] == "Indian" else 1)
    st.session_state["numbering_mode"] = "Indian" if "Indian" in numbering_mode else "International"

# ---------------------------------------------------------
# 3. SELECT ACTIVE DATAFRAME (Default vs Custom Uploaded)
# ---------------------------------------------------------
if st.session_state["data_source"] == "custom" and st.session_state["custom_df"] is not None:
    raw_df = st.session_state["custom_df"].copy()
    is_custom = True
    active_filename = st.session_state["custom_filename"]
else:
    try:
        raw_df = load_dataset()
        is_custom = False
        active_filename = "Built-in Retail Sales Dataset (Retail data.xlsx)"
    except Exception as e:
        st.error(f"Error loading base dataset: {e}")
        st.stop()

active_currency = st.session_state.get("currency_symbol", "₹")
active_numbering = st.session_state.get("numbering_mode", "Indian")

# ---------------------------------------------------------
# 4. ACTIVE DATASET MODE STATUS BANNER
# ---------------------------------------------------------
if is_custom:
    st.markdown(f"""
    <div class="mode-banner-custom">
        <div>
            <span style="font-weight:700; color:#10B981;">🟢 Custom Data Mode:</span> 
            <span style="color:#F8FAFC; font-weight:600;">{active_filename}</span> 
            <span style="color:#94A3B8; font-size:12px;">({len(raw_df):,} records &bull; Currency: {active_currency})</span>
        </div>
        <div style="font-size:12px; color:#A7F3D0;">Self-Service Ingestion Active</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="mode-banner-demo">
        <div>
            <span style="font-weight:700; color:#60A5FA;">🔵 Demo Mode:</span> 
            <span style="color:#F8FAFC; font-weight:600;">Built-in Business Dataset</span> 
            <span style="color:#94A3B8; font-size:12px;">({len(raw_df):,} records &bull; Currency: {active_currency})</span>
        </div>
        <div style="font-size:12px; color:#93C5FD;">Upload any Excel in the sidebar to switch datasets</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. TOP DASHBOARD SLICER BAR (Power BI Style at the Top)
# ---------------------------------------------------------
st.markdown("""
<div class="top-slicer-container">
    <div class="slicer-header">🎛️ Interactive Slicers</div>
</div>
""", unsafe_allow_html=True)

# Dynamically construct slicers based on available dimensions
has_date = "date" in raw_df.columns
has_region = "region" in raw_df.columns and raw_df["region"].nunique() > 1
has_product = "product" in raw_df.columns and raw_df["product"].nunique() > 1

col_s1, col_s2, col_s3 = st.columns(3)

if has_date:
    min_d = raw_df["date"].min().date()
    max_d = raw_df["date"].max().date()
    with col_s1:
        selected_dates = st.date_input("📅 Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d, key="slicer_date")
else:
    selected_dates = None
    with col_s1:
        st.info("📅 Date filter: Not applicable")

if has_region:
    available_regions = ["All"] + sorted(raw_df["region"].unique().tolist())
    with col_s2:
        selected_regions = st.multiselect("🌍 Region / Area", available_regions, default=["All"], key="slicer_region")
else:
    selected_regions = ["All"]
    with col_s2:
        st.info("🌍 Region filter: Single zone")

if has_product:
    available_products = ["All"] + sorted(raw_df["product"].unique().tolist())
    with col_s3:
        selected_products = st.multiselect("📦 Product / Category", available_products, default=["All"], key="slicer_product")
else:
    selected_products = ["All"]
    with col_s3:
        st.info("📦 Product filter: Single item")

# Filter Dataset
filtered_df = filter_dataset(
    raw_df,
    date_range=selected_dates if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2 else None,
    regions=selected_regions,
    products=selected_products
)

st.caption(f"🔍 Displaying **{len(filtered_df):,}** of **{len(raw_df):,}** records &bull; Number Format: `{active_numbering}`")
st.markdown("<hr style='margin: 8px 0 16px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("⚠️ No records match the active slicers. Please adjust your date range or filters.")
    st.stop()

# Compute active KPIs for filtered slice
current_kpis = calculate_kpis(filtered_df)

# =========================================================
# VIEW 1: 🏠 EXECUTIVE & PERFORMANCE OVERVIEW
# =========================================================
if navigation_page == "🏠 Executive & Performance":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Executive Performance & Decision Intelligence</div>
        <div class="hero-subtitle">High-level KPI performance, period-over-period variance decomposition, and health scorecard.</div>
    </div>
    """, unsafe_allow_html=True)

    # Core KPI Cards Row
    col1, col2, col3, col4 = st.columns(4)

    growth_val = current_kpis.get("growth_mom")
    if growth_val is not None:
        growth_delta = f"{growth_val:+.1f}% MoM"
        delta_class = "kpi-delta-positive" if growth_val >= 0 else "kpi-delta-negative"
    else:
        growth_delta = "Baseline Period"
        delta_class = "kpi-delta-neutral"

    with col1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">{format_business_number(current_kpis['total_revenue'], 'currency', active_currency, active_numbering)}</div>
            <div class="{delta_class}">{growth_delta}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        ord_val = current_kpis.get("order_growth_mom")
        ord_delta = f"{ord_val:+.1f}% MoM" if ord_val is not None else "Total Orders"
        ord_class = "kpi-delta-positive" if (ord_val is not None and ord_val >= 0) else "kpi-delta-neutral"
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Total Orders / Volume</div>
            <div class="kpi-value">{format_business_number(current_kpis['total_orders'], 'count', active_currency, active_numbering)}</div>
            <div class="{ord_class}">{ord_delta}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if current_kpis.get("has_profit"):
            prof_val = current_kpis.get("total_profit", 0.0)
            margin_pct = current_kpis.get("profit_margin_pct", 0.0)
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">Total Profit (Margin)</div>
                <div class="kpi-value">{format_business_number(prof_val, 'currency', active_currency, active_numbering)}</div>
                <div class="kpi-delta-positive">{margin_pct:.1f}% Profit Margin</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">Average Order Value (AOV)</div>
                <div class="kpi-value">{format_business_number(current_kpis['avg_order_value'], 'currency', active_currency, active_numbering)}</div>
                <div class="kpi-delta-neutral">Per Transaction</div>
            </div>
            """, unsafe_allow_html=True)

    with col4:
        health_summary = calculate_business_health_scorecard(filtered_df)
        score_val = health_summary.get("overall_score", 0)
        score_badge = "🟢 Healthy" if score_val >= 80 else ("🟡 Moderate" if score_val >= 60 else "🔴 At Risk")
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Business Health Score</div>
            <div class="kpi-value">{score_val} / 100</div>
            <div class="kpi-delta-neutral">{score_badge}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # STRUCTURED AI EXECUTIVE BRIEFING (No Raw Markdown / No Star Characters)
    with st.expander("🤖 **Generate Structured AI Executive Briefing**", expanded=False):
        if st.button("Generate Briefing", type="primary", key="btn_exec_summary"):
            with st.spinner("AI Analyst compiling verified business briefing..."):
                agent_res = process_agent_chat("Give me an executive CEO summary of business performance, growth, and risks.", filtered_df, currency_symbol=active_currency, numbering_mode=active_numbering)
                brief = agent_res.get("structured_brief", {})

                bullets_html = "".join([f"<div style='margin-bottom: 7px; line-height: 1.5;'>• {b}</div>" for b in brief.get('bullets', [])])
                actions_html = "".join([f"<div style='margin-bottom: 4px; line-height: 1.4;'><b>{i+1}.</b> {act}</div>" for i, act in enumerate(brief.get('actions', []))])

                st.markdown(f"""
                <div class="ai-brief-card">
                    <h4 style="margin:0 0 12px 0; color:#60A5FA; font-size: 16px;">📊 {brief.get('title', 'Executive Briefing')}</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 14px;">
                        {''.join([f'<div class="ai-metric-pill"><div class="ai-metric-pill-label">{m["label"]}</div><div class="ai-metric-pill-value">{m["value"]}</div></div>' for m in brief.get('metrics', [])])}
                    </div>
                    <div style="color: #E2E8F0; font-size: 13.5px;">
                        <div style="font-weight:700; color:#93C5FD; margin-bottom: 8px;">📌 Key Business Observations & Insights:</div>
                        {bullets_html}
                    </div>
                    <div style="color: #6EE7B7; font-size: 13px; margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.08);">
                        <div style="font-weight:700; margin-bottom: 6px;">🎯 Prioritized Strategic Focus Items:</div>
                        {actions_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.write("")

    # Revenue Trajectory + MoM Waterfall Driver Analysis
    row2_col1, row2_col2 = st.columns([1.4, 1])

    with row2_col1:
        st.markdown("### 📈 Revenue Velocity & Moving Averages")
        ts_data = get_time_series_trends(filtered_df, freq="D")
        fig_trend = plot_revenue_trend(ts_data, show_ma=True, currency_symbol=active_currency, numbering_mode=active_numbering)
        st.plotly_chart(fig_trend, use_container_width=True)

    with row2_col2:
        st.markdown("### 🔍 MoM Revenue Waterfall Drivers")
        decomp = perform_driver_decomposition(filtered_df)
        if decomp.get("can_decompose"):
            fig_waterfall = plot_revenue_waterfall(decomp.get("waterfall_items", []), currency_symbol=active_currency, numbering_mode=active_numbering)
            st.plotly_chart(fig_waterfall, use_container_width=True)
        else:
            st.info("Waterfall decomposition requires at least 2 distinct monthly periods.")

    # Business Health & Strategic Recommendations
    st.write("")
    tab_health, tab_recs = st.tabs(["🏥 Business Health Scorecard", "🎯 Strategic Action Recommendations"])

    with tab_health:
        for p in health_summary.get("pillars", []):
            st.markdown(f"""
            <div class="pillar-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #F8FAFC; font-size: 15px;">{p['name']}</span>
                    <span style="font-size: 13px; font-weight: 600;">{p['badge']} &bull; Score: {p['score']}/100</span>
                </div>
                <div style="color: #94A3B8; font-size: 13px; margin-top: 4px;"><b>Metric:</b> {p['metric']} &bull; {p['diagnostic']}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab_recs:
        recs = generate_strategic_recommendations(filtered_df)
        for r in recs:
            with st.expander(f"{r['badge']} — {r['category']}: {r['kpi']}", expanded=False):
                st.markdown(f"**Business Finding:** {r['business_interpretation']}")
                st.markdown(f"**Identified Risk:** {r['risk']}")
                st.markdown("**Action Items:**")
                for act in r["actions"]:
                    st.markdown(f"- {act}")

# =========================================================
# VIEW 2: 📦 PRODUCT & REGIONAL HUB
# =========================================================
elif navigation_page == "📦 Product & Regional Hub":
    st.markdown("## 📦 Product & Geographic Intelligence Hub")
    st.markdown("Evaluate category Pareto concentration, regional market share, and ticket size distributions.")

    prod_analysis = get_product_analysis(filtered_df)
    reg_analysis = get_regional_analysis(filtered_df)
    pareto_stats = get_pareto_summary(prod_analysis)

    # Top Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active Categories", f"{pareto_stats['total_categories']}")
    m2.metric("Top 5 Categories Share", f"{pareto_stats['top_5_share']:.1f}%")
    m3.metric("Active Regions", f"{len(reg_analysis)}")
    top_r_share = reg_analysis.iloc[0]["share_pct"] if not reg_analysis.empty else 0.0
    m4.metric("Leading Region Share", f"{top_r_share:.1f}%", reg_analysis.iloc[0]["region"] if not reg_analysis.empty else "N/A")

    st.write("")

    # Visualizations Row: Pareto & Regional Ranked Bar
    col_p, col_r = st.columns(2)

    with col_p:
        st.markdown("### 📊 Product Pareto 80/20 Analysis")
        fig_pareto = plot_product_pareto_chart(prod_analysis, top_n=15, currency_symbol=active_currency, numbering_mode=active_numbering)
        st.plotly_chart(fig_pareto, use_container_width=True)

    with col_r:
        st.markdown("### 🌍 Regional Revenue Contribution")
        fig_reg = plot_regional_ranked_bar(reg_analysis, top_n=12, metric="revenue", currency_symbol=active_currency, numbering_mode=active_numbering)
        st.plotly_chart(fig_reg, use_container_width=True)

    st.write("")

    # Treemap & Performance Tables
    tab_tree, tab_prod_tbl, tab_reg_tbl = st.tabs(["🌲 Hierarchy Treemap", "📋 Category League Table", "📋 Regional League Table"])

    with tab_tree:
        fig_tree = plot_product_treemap(filtered_df, top_n=15)
        st.plotly_chart(fig_tree, use_container_width=True)

    with tab_prod_tbl:
        st.dataframe(
            prod_analysis[["rank", "product", "revenue", "share_pct", "orders", "aov", "pareto_class"]],
            column_config={
                "rank": st.column_config.NumberColumn("Rank", format="%d"),
                "product": st.column_config.TextColumn("Category"),
                "revenue": st.column_config.NumberColumn("Revenue", format=f"{active_currency}%.2f"),
                "share_pct": st.column_config.NumberColumn("Share %", format="%.1f%%"),
                "orders": st.column_config.NumberColumn("Orders", format="%d"),
                "aov": st.column_config.NumberColumn("Avg Ticket", format=f"{active_currency}%.2f"),
                "pareto_class": st.column_config.TextColumn("Classification")
            },
            use_container_width=True,
            hide_index=True,
            height=400
        )

    with tab_reg_tbl:
        st.dataframe(
            reg_analysis[["rank", "region", "revenue", "share_pct", "orders", "aov"]],
            column_config={
                "rank": st.column_config.NumberColumn("Rank", format="%d"),
                "region": st.column_config.TextColumn("Region"),
                "revenue": st.column_config.NumberColumn("Revenue", format=f"{active_currency}%.2f"),
                "share_pct": st.column_config.NumberColumn("Share %", format="%.1f%%"),
                "orders": st.column_config.NumberColumn("Orders", format="%d"),
                "aov": st.column_config.NumberColumn("Avg Ticket", format=f"{active_currency}%.2f")
            },
            use_container_width=True,
            hide_index=True,
            height=400
        )

# =========================================================
# VIEW 3: 📈 FORECAST & ANOMALY CENTER
# =========================================================
elif navigation_page == "📈 Forecast & Anomaly Center":
    st.markdown("## 📈 Forward Forecasting & Anomaly Incident Center")
    st.markdown("Prophet time-series demand forecasting with confidence intervals and statistical Z-score anomaly incident detection.")

    tab_fc, tab_anom = st.tabs(["🔮 Revenue Forecasting (Prophet)", "🚨 Anomaly Incident Detection"])

    with tab_fc:
        fc_col1, fc_col2 = st.columns([1, 3])
        with fc_col1:
            horizon_choice = st.radio("Forecast Horizon", [30, 60, 90], index=0, format_func=lambda x: f"{x} Days Ahead")

        with st.spinner("Computing time-series forecast..."):
            forecast_results = generate_revenue_forecast(filtered_df, horizon_days=horizon_choice)

        if forecast_results.get("has_data"):
            f1, f2, f3 = st.columns(3)
            f1.metric("Projected Total Revenue", format_business_number(forecast_results['projected_total_revenue'], 'currency', active_currency, active_numbering))
            f2.metric("Projected Daily Run-Rate", format_business_number(forecast_results['projected_avg_daily'], 'currency', active_currency, active_numbering) + "/day")
            f3.metric("Projected Growth over Baseline", f"{forecast_results['projected_growth_pct']:+.1f}%")

            st.plotly_chart(plot_forecast_intervals(forecast_results["forecast_df"], currency_symbol=active_currency, numbering_mode=active_numbering), use_container_width=True)
        else:
            st.warning(forecast_results.get("message", "Unable to generate forecast."))

    with tab_anom:
        z_thresh = st.slider("Z-Score Sensitivity (|Z|)", min_value=1.5, max_value=3.5, value=2.0, step=0.1)
        anomalies_df = detect_anomalies(filtered_df, z_threshold=z_thresh)
        ts_daily = get_time_series_trends(filtered_df, freq="D")
        total_days = filtered_df["date"].dt.normalize().nunique() if "date" in filtered_df.columns else 1
        a_metrics = get_anomaly_summary_metrics(anomalies_df, total_days=total_days)

        a1, a2, a3 = st.columns(3)
        a1.metric("Anomalies Detected", f"{a_metrics['total_anomalies']}")
        a2.metric("Positive Spikes", f"{a_metrics['spikes_count']}", "High Volume")
        a3.metric("Contraction Drops", f"{a_metrics['drops_count']}", "Low Volume")

        st.plotly_chart(plot_anomaly_timeline(ts_daily, anomalies_df, currency_symbol=active_currency, numbering_mode=active_numbering), use_container_width=True)

        if not anomalies_df.empty:
            explanations = explain_anomaly(filtered_df, anomalies_df)
            with st.expander("📋 View Anomaly Incident Log & Explanations", expanded=False):
                for exp in explanations:
                    st.info(exp)

# =========================================================
# VIEW 4: 🤖 AI BUSINESS ANALYST (Chat)
# =========================================================
elif navigation_page == "🤖 AI Business Analyst (Chat)":
    st.markdown("## 🤖 AI Business Analyst Agent")
    st.markdown("Ask natural language business questions. Powered by verified Python analytics & Groq LLM reasoning.")

    # Suggested Prompts Chips
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    if p_col1.button("💡 Executive CEO summary", use_container_width=True):
        st.session_state["chat_input_val"] = "Give me a CEO summary of business performance."
    if p_col2.button("💡 Why did revenue decline?", use_container_width=True):
        st.session_state["chat_input_val"] = "Why did revenue decline and what caused it?"
    if p_col3.button("💡 What are top products?", use_container_width=True):
        st.session_state["chat_input_val"] = "What are my top products and Pareto distribution?"
    if p_col4.button("💡 Show detected anomalies", use_container_width=True):
        st.session_state["chat_input_val"] = "Show me detected revenue anomalies."

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div><div style="clear:both"></div>', unsafe_allow_html=True)
        else:
            if msg.get("is_card"):
                st.markdown(msg["content"], unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-bubble">{msg["content"]}</div><div style="clear:both"></div>', unsafe_allow_html=True)

    st.write("")

    user_query = st.chat_input("Ask any business or dataset question...")
    if "chat_input_val" in st.session_state and st.session_state["chat_input_val"]:
        user_query = st.session_state.pop("chat_input_val")

    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.markdown(f'<div class="user-bubble">{user_query}</div><div style="clear:both"></div>', unsafe_allow_html=True)

        with st.spinner("AI Analyst analyzing verified metrics..."):
            agent_out = process_agent_chat(user_query, filtered_df, st.session_state.chat_history, currency_symbol=active_currency, numbering_mode=active_numbering)
            brief = agent_out.get("structured_brief", {})
            bullets = brief.get("bullets", [])
            actions = brief.get("actions", [])

            bullets_html = "".join([f"<div style='margin-bottom: 7px; line-height: 1.5;'>• {b}</div>" for b in bullets])
            actions_html = "".join([f"<div style='margin-bottom: 4px; line-height: 1.4;'><b>{i+1}.</b> {act}</div>" for i, act in enumerate(actions)])

            # Render clean structured card in chat
            response_html = f"""
            <div class="ai-brief-card">
                <div style="font-weight:700; color:#60A5FA; font-size: 15px; margin-bottom:10px;">📊 {brief.get('title', 'AI Business Analysis')}</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 8px; margin-bottom: 12px;">
                    {''.join([f'<div class="ai-metric-pill"><div class="ai-metric-pill-label">{m["label"]}</div><div class="ai-metric-pill-value">{m["value"]}</div></div>' for m in brief.get('metrics', [])])}
                </div>
                <div style="color: #E2E8F0; font-size: 13.5px;">
                    <div style="font-weight:700; color:#93C5FD; margin-bottom: 8px;">📌 Key Observations & Insights:</div>
                    {bullets_html}
                </div>
                {f'''<div style="color: #6EE7B7; font-size: 13px; margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.08);">
                    <div style="font-weight:700; margin-bottom: 6px;">🎯 Prioritized Action Items:</div>
                    {actions_html}
                </div>''' if actions else ''}
            </div>
            """
            st.session_state.chat_history.append({"role": "assistant", "content": response_html, "is_card": True})
            st.markdown(response_html, unsafe_allow_html=True)

# =========================================================
# VIEW 5: 🔎 DATA EXPLORER & QUALITY
# =========================================================
elif navigation_page == "🔎 Data Explorer & Quality":
    st.markdown("## 🔎 Data Quality Audit & Interactive Explorer")
    st.markdown("Audit data integrity, completeness, and export filtered datasets and reports.")

    tab_exp, tab_dq, tab_dl = st.tabs(["📋 Filtered Data Explorer", "🛡️ Data Quality Audit", "📥 1-Click Exports"])

    with tab_exp:
        display_cols = [c for c in ["date", "region", "product", "revenue", "profit", "quantity", "month"] if c in filtered_df.columns]
        st.dataframe(
            filtered_df[display_cols],
            column_config={
                "date": st.column_config.DatetimeColumn("Date", format="YYYY-MM-DD HH:mm"),
                "region": st.column_config.TextColumn("Region"),
                "product": st.column_config.TextColumn("Product Category"),
                "revenue": st.column_config.NumberColumn("Revenue", format=f"{active_currency}%.2f"),
                "profit": st.column_config.NumberColumn("Profit", format=f"{active_currency}%.2f"),
                "quantity": st.column_config.NumberColumn("Quantity", format="%.0f"),
                "month": st.column_config.TextColumn("Month")
            },
            use_container_width=True,
            hide_index=True,
            height=420
        )

    with tab_dq:
        dq_report = calculate_data_quality_report(filtered_df)
        st.markdown(f"### Data Integrity Score: **{dq_report['overall_score']} / 100**")
        for diag in dq_report.get("diagnostics", []):
            st.markdown(f"• **{diag['dimension']}**: {diag['status']} ({diag['metric']}) — *{diag['detail']}*")

    with tab_dl:
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=export_df_to_csv(filtered_df),
                file_name="filtered_business_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        with d2:
            kpi_txt = generate_kpi_summary_report(current_kpis, calculate_business_health_scorecard(filtered_df))
            st.download_button(
                label="📥 Download Executive KPI Report (TXT)",
                data=kpi_txt.encode("utf-8"),
                file_name="executive_kpi_report.md",
                mime="text/markdown",
                use_container_width=True
            )
