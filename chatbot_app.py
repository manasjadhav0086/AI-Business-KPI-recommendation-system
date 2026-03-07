import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Business Analytics Platform",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM STYLING
# -------------------------------------------------
st.markdown("""
<style>

.big-title{
    font-size:36px;
    font-weight:700;
}

.kpi-card{
    padding:25px;
    border-radius:12px;
    background: linear-gradient(135deg,#1f2937,#111827);
    text-align:center;
    color:white;
    box-shadow:0px 6px 10px rgba(0,0,0,0.3);
}

.kpi-title{
    font-size:16px;
    opacity:0.8;
}

.kpi-value{
    font-size:34px;
    font-weight:700;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------
# username = "root"
# password = "Manas0086"
# host = "localhost"
# database = "ai_business_kpi"

# engine = create_engine(
#    f"mysql+pymysql://{username}:{password}@{host}/{database}"
#)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
#data = pd.read_sql("SELECT * FROM processed_business_data", engine)
#forecast = pd.read_sql("SELECT * FROM revenue_forecast", engine)

@st.cache_data
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/manasjadhav0086/AI-Business-KPI-recommendation-system/refs/heads/main/Bussiness_data.csv")
    return df

data = load_data()

data["date"] = pd.to_datetime(data["date"])
# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.title("AI Analytics Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Dashboard",
        "Revenue Analysis",
        "AI Chatbot"
    ]
)

# =================================================
# EXECUTIVE DASHBOARD
# =================================================
if page == "Executive Dashboard":

    st.markdown('<p class="big-title">Executive Business Dashboard</p>', unsafe_allow_html=True)

    total_revenue = data["revenue"].sum()
    total_orders = data.shape[0]
    total_regions = data["region"].nunique()

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div class="kpi-card">
    <div class="kpi-title">Total Revenue</div>
    <div class="kpi-value">{total_revenue:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="kpi-card">
    <div class="kpi-title">Total Orders</div>
    <div class="kpi-value">{total_orders}</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="kpi-card">
    <div class="kpi-title">Regions</div>
    <div class="kpi-value">{total_regions}</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # -------------------------------------------------
    # MONTHLY REVENUE TREND
    # -------------------------------------------------
    monthly_revenue = (
        data.groupby(pd.Grouper(key="date", freq="M"))["revenue"]
        .sum()
        .reset_index()
    )

    monthly_revenue["month"] = monthly_revenue["date"].dt.strftime("%b %Y")

    fig = px.line(
        monthly_revenue,
        x="month",
        y="revenue",
        markers=True
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<p style='text-align:center;font-weight:600'>Monthly Revenue Trend</p>",
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # MONTHLY FORECAST
    # -------------------------------------------------
    if not forecast.empty:

        forecast["ds"] = pd.to_datetime(forecast["ds"])

        monthly_forecast = (
            forecast.groupby(pd.Grouper(key="ds", freq="M"))["yhat"]
            .mean()
            .reset_index()
        )

        monthly_forecast["month"] = monthly_forecast["ds"].dt.strftime("%b %Y")

        fig2 = px.line(
            monthly_forecast,
            x="month",
            y="yhat",
            markers=True
        )

        fig2.update_layout(height=450)

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown(
            "<p style='text-align:center;font-weight:600'>Monthly Revenue Forecast</p>",
            unsafe_allow_html=True
        )

# =================================================
# REVENUE ANALYSIS
# =================================================
elif page == "Revenue Analysis":

    st.title("Revenue Analysis")

    col1, col2 = st.columns(2)

    # Revenue by Region
    region_data = (
        data.groupby("region")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    fig_region = px.bar(
        region_data,
        x="region",
        y="revenue"
    )

    fig_region.update_layout(height=450)

    col1.plotly_chart(fig_region, use_container_width=True)

    col1.markdown(
        "<p style='text-align:center;font-weight:600'>Revenue by Region</p>",
        unsafe_allow_html=True
    )

    # Revenue by Product
    product_data = (
        data.groupby("product")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    fig_product = px.pie(
        product_data,
        names="product",
        values="revenue"
    )

    fig_product.update_layout(height=450)

    col2.plotly_chart(fig_product, use_container_width=True)

    col2.markdown(
        "<p style='text-align:center;font-weight:600'>Revenue by Product</p>",
        unsafe_allow_html=True
    )

# =================================================
# AI CHATBOT
# =================================================
elif page == "AI Chatbot":

    st.title("AI Business Chatbot")

    question = st.text_input("Ask a question about your data")

    def answer_question(q):

        q = q.lower()

        # BEST REGION
        if "best region" in q or "top region" in q:

            region_rev = (
                data.groupby("region")["revenue"]
                .sum()
                .sort_values(ascending=False)
            )

            region = region_rev.idxmax()
            value = region_rev.max()

            return f"Top performing region is **{region}** with revenue **{value:,.0f}**."

        # WORST REGION
        elif "worst region" in q:

            region_rev = (
                data.groupby("region")["revenue"]
                .sum()
                .sort_values()
            )

            region = region_rev.idxmin()
            value = region_rev.min()

            return f"Worst performing region is **{region}** with revenue **{value:,.0f}**."

        # BEST PRODUCT
        elif "best product" in q or "top product" in q:

            product_rev = (
                data.groupby("product")["revenue"]
                .sum()
                .sort_values(ascending=False)
            )

            product = product_rev.idxmax()
            value = product_rev.max()

            return f"Best performing product category is **{product}** with revenue **{value:,.0f}**."

        # WORST PRODUCT
        elif "worst product" in q:

            product_rev = (
                data.groupby("product")["revenue"]
                .sum()
                .sort_values()
            )

            product = product_rev.idxmin()
            value = product_rev.min()

            return f"Worst performing product category is **{product}** with revenue **{value:,.0f}**."

        # TOTAL REVENUE
        elif "revenue" in q:

            total = data["revenue"].sum()

            return f"Total revenue generated is **{total:,.0f}**."

        # TREND
        elif "trend" in q:

            monthly = (
                data.groupby(pd.Grouper(key="date", freq="M"))["revenue"]
                .sum()
                .reset_index()
            )

            last_month = monthly.iloc[-1]["revenue"]
            prev_month = monthly.iloc[-2]["revenue"]

            change = ((last_month - prev_month) / prev_month) * 100

            return f"Revenue changed by **{change:.2f}%** compared to last month."

        else:

            return "Try asking: best product, worst product, best region, worst region, revenue trend."

    if question:

        response = answer_question(question)


        st.success(response)
