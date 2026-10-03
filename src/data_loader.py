import os
import pandas as pd
import streamlit as st
from src.db_connection import get_connection

@st.cache_data(show_spinner=False)
def load_dataset(file_path: str = "Retail data.xlsx") -> pd.DataFrame:
    """
    Loads and normalizes the default business dataset (Retail data.xlsx).
    Falls back to Bussiness_data.csv if Excel is unavailable.
    """
    df = None
    
    # 1. Primary path: Local Retail data.xlsx
    if os.path.exists("Retail data.xlsx"):
        try:
            df = pd.read_excel("Retail data.xlsx", sheet_name="Raw Sales Data")
        except Exception:
            df = pd.read_excel("Retail data.xlsx")
    elif os.path.exists("Bussiness_data.csv"):
        df = pd.read_csv("Bussiness_data.csv")
    else:
        # Fallback to MySQL / remote
        try:
            engine = get_connection()
            with engine.connect() as conn:
                orders = pd.read_sql("SELECT * FROM orders", conn)
                items = pd.read_sql("SELECT * FROM order_items", conn)
                customers = pd.read_sql("SELECT * FROM customers", conn)
                products = pd.read_sql("SELECT * FROM products", conn)

                merged = orders.merge(items, on="order_id")
                merged = merged.merge(customers, on="customer_id")
                merged = merged.merge(products, on="product_id")
                df = merged
        except Exception:
            remote_url = "https://raw.githubusercontent.com/manasjadhav0086/AI-Business-KPI-recommendation-system/main/Bussiness_data.csv"
            df = pd.read_csv(remote_url)

    # Standardize column mappings for Retail data.xlsx & legacy datasets
    df = df.rename(columns={
        "Order Date": "date",
        "Order_Date": "date",
        "order_purchase_timestamp": "date",
        "Category": "product",
        "Product Name": "product_name",
        "Product": "product",
        "product_category_name": "product",
        "Region": "region",
        "customer_state": "region",
        "Sales Amount": "revenue",
        "Revenue": "revenue",
        "price": "revenue",
        "Profit Amount": "profit",
        "Profit": "profit",
        "Quantity": "quantity",
        "Customer Name": "customer",
        "Customer Segment": "segment",
        "City": "city",
        "Channel": "channel",
        "Unit Price": "unit_price",
        "Cost Amount": "cost",
        "Discount %": "discount",
        "Payment Method": "payment_method"
    })

    # Clean and parse types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    
    # Fill product and region cleanly
    df["product"] = df["product"].fillna("General Item").astype(str).str.strip()
    df["region"] = df["region"].fillna("General Region").astype(str).str.strip().str.upper()
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0.0)

    if "profit" in df.columns:
        df["profit"] = pd.to_numeric(df["profit"], errors="coerce").fillna(0.0)

    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1.0)
    else:
        df["quantity"] = 1.0

    # Add normalized date and calendar dimensions
    df["date_only"] = df["date"].dt.normalize()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["day_name"] = df["date"].dt.day_name()
    df["month_name"] = df["date"].dt.strftime("%b %Y")

    # Sort chronologically
    df = df.sort_values("date").reset_index(drop=True)
    return df

def filter_dataset(
    df: pd.DataFrame,
    date_range: tuple = None,
    regions: list = None,
    products: list = None,
    min_revenue: float = None,
    max_revenue: float = None
) -> pd.DataFrame:
    """
    Applies multi-dimensional filters on the dataset.
    """
    filtered = df.copy()

    if date_range and len(date_range) == 2 and date_range[0] and date_range[1]:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        filtered = filtered[(filtered["date"] >= start_date) & (filtered["date"] <= end_date)]

    if regions and len(regions) > 0 and "All" not in regions:
        filtered = filtered[filtered["region"].isin(regions)]

    if products and len(products) > 0 and "All" not in products:
        filtered = filtered[filtered["product"].isin(products)]

    if min_revenue is not None:
        filtered = filtered[filtered["revenue"] >= min_revenue]

    if max_revenue is not None:
        filtered = filtered[filtered["revenue"] <= max_revenue]

    return filtered
