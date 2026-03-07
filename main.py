from src.data_pipeline import load_data
from src.kpi_engine import calculate_kpis
from src.forecasting import revenue_forecast
from src.anomaly_detection import detect_anomalies
from src.root_cause import root_cause_analysis
from src.llm_insight_generator import generate_insight

import pandas as pd

# Load data
df = load_data()

# KPI calculation
kpis = calculate_kpis(df)

# Forecasting
forecast = revenue_forecast(df)

# Anomaly detection
anomalies = detect_anomalies(df)

# Root cause detection
region, product = root_cause_analysis(df)

# Simulated revenue change
change = -12

# Generate AI insight
insight = generate_insight(change, region, product)

insight_df = pd.DataFrame({
    "Insight":[insight]
})

print(insight_df)

insight_df.to_csv("outputs/ai_insights.txt",index=False)