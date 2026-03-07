import pandas as pd

def root_cause_analysis(df):

    months = sorted(df["month"].unique())

    if len(months) < 2:
        return None, None

    current_month = months[-1]
    previous_month = months[-2]

    current_data = df[df["month"] == current_month]
    previous_data = df[df["month"] == previous_month]

    region_current = current_data.groupby("region")["revenue"].sum()
    region_previous = previous_data.groupby("region")["revenue"].sum()

    region_change = region_current - region_previous

    worst_region = region_change.idxmin()

    product_current = current_data.groupby("product")["revenue"].sum()
    product_previous = previous_data.groupby("product")["revenue"].sum()

    product_change = product_current - product_previous

    worst_product = product_change.idxmin()

    return worst_region, worst_product