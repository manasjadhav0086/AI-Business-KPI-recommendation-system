def calculate_kpis(df):

    total_revenue = df["revenue"].sum()

    revenue_by_region = df.groupby("region")["revenue"].sum()

    revenue_by_product = df.groupby("product")["revenue"].sum()

    return {
        "total_revenue": total_revenue,
        "region": revenue_by_region,
        "product": revenue_by_product
    }