import pandas as pd

from src.data_pipeline import load_data
from src.kpi_engine import calculate_kpis
from src.forecasting import revenue_forecast
from src.anomaly_detection import detect_anomalies
from src.anomaly_explainer import explain_anomaly
from src.root_cause import root_cause_analysis
from src.llm_insight_generator import generate_insight
from src.kpi_recommender import generate_recommendation
from src.db_connection import get_connection


print("\nStarting AI Business KPI Pipeline...\n")

# -------------------------------------------------
# 1️⃣ Load data from MySQL
# -------------------------------------------------
df = load_data()

print("Dataset Loaded Successfully")
print("Total Rows:", len(df))
print(df.head())


# -------------------------------------------------
# 2️⃣ Save processed dataset
# -------------------------------------------------
engine = get_connection()

df.to_sql(
    "processed_business_data",
    engine,
    if_exists="replace",
    index=False
)


# -------------------------------------------------
# 3️⃣ KPI Calculation
# -------------------------------------------------
kpis = calculate_kpis(df)

print("\nKPI Summary")
print("Total Revenue:", kpis["total_revenue"])


# -------------------------------------------------
# 4️⃣ Forecast Future Revenue
# -------------------------------------------------
forecast = revenue_forecast(df)

print("\nRevenue Forecast Completed")


# -------------------------------------------------
# 5️⃣ Detect Revenue Anomalies
# -------------------------------------------------
anomalies = detect_anomalies(df)

print("\nAnomalies Detected:", len(anomalies))


# -------------------------------------------------
# 6️⃣ Explain Anomalies with AI logic
# -------------------------------------------------
anomaly_explanations = explain_anomaly(df, anomalies)

for exp in anomaly_explanations:
    print("\nAI Anomaly Explanation:\n")
    print(exp)


# Save anomaly explanations
anomaly_df = pd.DataFrame({
    "explanation": anomaly_explanations
})

anomaly_df.to_csv(
    "outputs/anomaly_explanations.csv",
    index=False
)

anomaly_df.to_sql(
    "ai_anomaly_explanations",
    engine,
    if_exists="replace",
    index=False
)


# -------------------------------------------------
# 7️⃣ Root Cause Detection
# -------------------------------------------------
region, product = root_cause_analysis(df)

if region is None:
    region = "overall market"

if product is None:
    product = "multiple product categories"


# -------------------------------------------------
# 8️⃣ Calculate Revenue Change (Month-over-Month)
# -------------------------------------------------
monthly_revenue = (
    df.groupby("month")["revenue"]
    .sum()
    .reset_index()
)

change = 0

if len(monthly_revenue) >= 2:

    last_month = monthly_revenue.iloc[-1]["revenue"]
    previous_month = monthly_revenue.iloc[-2]["revenue"]

    change = ((last_month - previous_month) / previous_month) * 100


# -------------------------------------------------
# 9️⃣ Generate AI Insight
# -------------------------------------------------
insight = generate_insight(change, region, product)

print("\nAI Business Insight:\n")
print(insight)


# -------------------------------------------------
# 🔟 Generate Business Recommendation
# -------------------------------------------------
recommendation = generate_recommendation(change, region, product)

print("\nBusiness Recommendation:\n")
print(recommendation)


# -------------------------------------------------
# 1️⃣1️⃣ Save AI Results
# -------------------------------------------------
result_df = pd.DataFrame({
    "insight": [insight],
    "recommendation": [recommendation]
})

result_df.to_csv(
    "outputs/ai_business_recommendations.csv",
    index=False
)

result_df.to_sql(
    "ai_business_recommendations",
    engine,
    if_exists="replace",
    index=False
)


print("\nPipeline Completed Successfully")
print("\nOutputs saved to:")
print("outputs/ folder and MySQL tables")