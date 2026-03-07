import pandas as pd

def load_data():

    orders = pd.read_csv("data/raw/olist_orders_dataset.csv")
    items = pd.read_csv("data/raw/olist_order_items_dataset.csv")
    customers = pd.read_csv("data/raw/olist_customers_dataset.csv")
    products = pd.read_csv("data/raw/olist_products_dataset.csv")

    # Merge tables
    df = orders.merge(items, on="order_id")
    df = df.merge(customers, on="customer_id")
    df = df.merge(products, on="product_id")

    # Convert date
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"]
    )

    # Create analytical dataset
    df_final = df[[
        "order_purchase_timestamp",
        "customer_state",
        "product_category_name",
        "price"
    ]]

    df_final = df_final.rename(columns={
        "order_purchase_timestamp": "date",
        "customer_state": "region",
        "product_category_name": "product",
        "price": "revenue"
    })

    df_final["month"] = df_final["date"].dt.to_period("M")

    # Save processed data
    df_final.to_csv("data/processed/business_data.csv", index=False)

    return df_final