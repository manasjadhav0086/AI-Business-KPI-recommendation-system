import pandas as pd
from src.db_connection import get_connection

def load_data():

    engine = get_connection()

    orders = pd.read_sql("SELECT * FROM orders", engine)
    items = pd.read_sql("SELECT * FROM order_items", engine)
    customers = pd.read_sql("SELECT * FROM customers", engine)
    products = pd.read_sql("SELECT * FROM products", engine)

    df = orders.merge(items,on="order_id")
    df = df.merge(customers,on="customer_id")
    df = df.merge(products,on="product_id")

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"]
    )

    df_final = df[[
        "order_purchase_timestamp",
        "customer_state",
        "product_category_name",
        "price"
    ]]

    df_final = df_final.rename(columns={
        "order_purchase_timestamp":"date",
        "customer_state":"region",
        "product_category_name":"product",
        "price":"revenue"
    })

    df_final["month"] = df_final["date"].dt.to_period("M")

    return df_final