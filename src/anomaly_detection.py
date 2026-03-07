import pandas as pd

def detect_anomalies(df):

    revenue = df.groupby("date")["revenue"].sum()

    mean = revenue.mean()

    std = revenue.std()

    zscore = (revenue - mean) / std

    anomalies = revenue[zscore.abs() > 2]

    anomaly_df = anomalies.reset_index()

    anomaly_df.to_csv("outputs/anomaly_data.csv", index=False)

    return anomaly_df