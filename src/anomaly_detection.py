import pandas as pd
from src.db_connection import get_connection


def detect_anomalies(df):

    # Aggregate daily revenue
    revenue = df.groupby("date")["revenue"].sum().reset_index()

    revenue["mean"] = revenue["revenue"].mean()
    revenue["std"] = revenue["revenue"].std()

    revenue["zscore"] = (
        (revenue["revenue"] - revenue["mean"]) /
        revenue["std"]
    )

    anomalies = revenue[revenue["zscore"].abs() > 2]

    print("\nAnomalies detected:", len(anomalies))

    # Save anomalies
    anomalies.to_csv("outputs/anomaly_data.csv", index=False)

    try:
        engine = get_connection()
        anomalies.to_sql(
            "revenue_anomalies",
            engine,
            if_exists="replace",
            index=False
        )
    except Exception as e:
        print(f"Notice: Could not write revenue_anomalies to MySQL ({e}). Saved to CSV.")

    return anomalies