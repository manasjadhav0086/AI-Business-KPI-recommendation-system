def explain_anomaly(df, anomalies):

    explanations = []

    for _, row in anomalies.iterrows():

        anomaly_date = row["date"]

        day_data = df[df["date"] == anomaly_date]

        region_sales = (
            day_data.groupby("region")["revenue"]
            .sum()
            .idxmax()
        )

        product_sales = (
            day_data.groupby("product")["revenue"]
            .sum()
            .idxmax()
        )

        explanation = f"""
Anomaly detected on {anomaly_date}.

Revenue significantly deviated from the normal trend.

The spike was mainly driven by strong sales
in the {product_sales} category in the {region_sales} region.

Possible causes include promotional campaigns,
seasonal demand, or regional marketing events.
"""

        explanations.append(explanation.strip())

    return explanations