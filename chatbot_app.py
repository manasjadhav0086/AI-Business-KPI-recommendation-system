import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet

st.set_page_config(page_title="AI Business KPI Chatbot", layout="wide")

st.title("🤖 AI Business KPI Recommendation System")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed_business_data.csv")
    return df

data = load_data()

# -------------------------------
# Convert Date
# -------------------------------
data["order_purchase_timestamp"] = pd.to_datetime(data["order_purchase_timestamp"])
data["month"] = data["order_purchase_timestamp"].dt.to_period("M").astype(str)

# -------------------------------
# KPI Calculations
# -------------------------------
total_revenue = data["payment_value"].sum()
total_orders = data["order_id"].nunique()
total_customers = data["customer_unique_id"].nunique()
avg_order_value = total_revenue / total_orders

col1,col2,col3,col4 = st.columns(4)

col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Orders", total_orders)
col3.metric("Customers", total_customers)
col4.metric("Avg Order Value", f"${avg_order_value:,.2f}")

st.divider()

# -------------------------------
# Monthly Revenue
# -------------------------------
monthly_revenue = (
    data.groupby("month")["payment_value"]
    .sum()
    .reset_index()
)

fig = px.line(
    monthly_revenue,
    x="month",
    y="payment_value",
    title="Monthly Revenue Trend"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Best Product
# -------------------------------
product_sales = (
    data.groupby("product_category_name")["payment_value"]
    .sum()
    .reset_index()
)

best_product = product_sales.loc[
    product_sales["payment_value"].idxmax()
]

worst_product = product_sales.loc[
    product_sales["payment_value"].idxmin()
]

col1,col2 = st.columns(2)

col1.metric(
    "🏆 Best Product",
    best_product["product_category_name"],
    f"${best_product['payment_value']:,.0f}"
)

col2.metric(
    "⚠️ Worst Product",
    worst_product["product_category_name"],
    f"${worst_product['payment_value']:,.0f}"
)

# -------------------------------
# Forecasting
# -------------------------------
st.subheader("📈 Revenue Forecast")

forecast_df = monthly_revenue.rename(
    columns={
        "month":"ds",
        "payment_value":"y"
    }
)

forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])

model = Prophet()
model.fit(forecast_df)

future = model.make_future_dataframe(periods=6, freq="M")

forecast = model.predict(future)

forecast_chart = px.line(
    forecast,
    x="ds",
    y="yhat",
    title="Revenue Forecast (Next 6 Months)"
)

st.plotly_chart(forecast_chart, use_container_width=True)

# -------------------------------
# AI Chatbot
# -------------------------------
st.subheader("💬 Ask Business Questions")

user_input = st.text_input(
    "Ask something like: best product, worst product, revenue trend..."
)

def generate_answer(question):

    question = question.lower()

    if "best product" in question:
        return f"""
        The best performing product category is **{best_product['product_category_name']}**
        with revenue of **${best_product['payment_value']:,.2f}**.
        """

    elif "worst product" in question:
        return f"""
        The worst performing product category is **{worst_product['product_category_name']}**
        with revenue of **${worst_product['payment_value']:,.2f}**.
        """

    elif "revenue" in question:
        return f"""
        Total revenue generated is **${total_revenue:,.2f}**
        across **{total_orders} orders**.
        """

    elif "customers" in question:
        return f"""
        Total unique customers are **{total_customers}**.
        """

    elif "forecast" in question:
        return """
        Revenue forecast has been generated for the next **6 months**
        using Prophet time series forecasting.
        """

    else:
        return """
        I can help with:
        • Best Product
        • Worst Product
        • Revenue
        • Forecast
        • Customers
        """

if user_input:
    response = generate_answer(user_input)
    st.success(response)

# -------------------------------
# Top Products Chart
# -------------------------------
st.subheader("📊 Top Product Categories")

top_products = product_sales.sort_values(
    "payment_value",
    ascending=False
).head(10)

fig = px.bar(
    top_products,
    x="payment_value",
    y="product_category_name",
    orientation="h",
    title="Top 10 Product Categories"
)

st.plotly_chart(fig, use_container_width=True)
