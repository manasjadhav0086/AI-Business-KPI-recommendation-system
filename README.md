# 🚀 AI-Powered Business KPI Recommendation Platform

An end-to-end **AI analytics platform** that automatically analyzes business KPIs, detects anomalies, forecasts revenue, and generates actionable insights for executives.

🔗 **Live Application:** [https://ai-analytics-platform.streamlit.app/](https://ai-analytics-platform.streamlit.app/)

---

# 📌 Business Problem

Executives often struggle to interpret dashboards and understand **why key metrics change**.

Traditional dashboards only show:

```
Revenue ↓ 12%
```

But they do not answer:

* Why did revenue change?
* Which region or product caused it?
* What should the business do next?

---

# 💡 Solution

This platform automatically analyzes business data and provides **AI-generated insights and recommendations**.

Example output:

```
Revenue declined by 12% mainly due to weak electronics sales
in the SP region and reduced repeat customers.

Recommendation:
Increase targeted promotions and inventory in high-demand regions.
```

---

# 🧠 System Architecture

```
MySQL Data Warehouse
        ↓
Python ETL Pipeline
        ↓
KPI Engine
        ↓
Revenue Forecasting (Prophet)
        ↓
Anomaly Detection
        ↓
Root Cause Analysis
        ↓
AI Insight Generator
        ↓
Streamlit Analytics Dashboard + Chatbot
```

---

# 📊 Features

### Executive Analytics Dashboard

* Revenue KPIs
* Monthly revenue trend
* Forecasted revenue
* Regional performance analysis
* Product performance insights

---

### 📈 Revenue Forecasting

Uses **Facebook Prophet** to forecast future revenue trends.

Example:

```
Actual Revenue vs Forecast Revenue
```

This helps businesses **anticipate demand and plan inventory or marketing campaigns**.

---

### ⚠️ Anomaly Detection

Automatically detects unusual spikes or drops in revenue.

Example:

```
Anomaly detected on 2017-11-24.

Revenue increased 85% due to high Black Friday sales.
```

---

### 🔍 Root Cause Analysis

Identifies which **region or product category** caused KPI changes.

Example:

```
Revenue drop mainly driven by decline in electronics sales in SP region.
```

---

### 🤖 AI Business Recommendations

The system generates recommendations for executives:

```
Increase promotional campaigns for electronics
in underperforming regions.
```

---

### 💬 AI Analytics Chatbot

Users can ask business questions such as:

```
Which region has the highest revenue?
Which product performs worst?
How is revenue trending?
```

The chatbot analyzes data and returns insights instantly.

---

# 🛠 Tech Stack

### Data Engineering

* Python
* Pandas
* SQL
* MySQL

### Machine Learning

* Prophet (time-series forecasting)

### Data Analytics

* KPI calculation
* anomaly detection
* root cause analysis

### Visualization

* Streamlit
* Plotly
* Power BI

---

# 📂 Project Structure

```
AI-Business-KPI-Recommendation-System

data/
datasets used for analysis

src/
data_pipeline.py
kpi_engine.py
forecasting.py
anomaly_detection.py
root_cause_analysis.py
llm_insight_generator.py

streamlit_app.py
interactive analytics dashboard

main.py
end-to-end pipeline

outputs/
generated insights and forecasts
```

---

# 📊 Dashboard Preview

Key components:

```
Executive KPI Dashboard
Monthly Revenue Trend
Revenue Forecast
Revenue by Region
Revenue by Product
AI Insights & Recommendations
```

---

# 🚀 How to Run the Project

### 1️⃣ Clone the repository

```
git clone https://github.com/yourusername/AI-Business-KPI-Recommendation-System
```

---

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

---

### 3️⃣ Run the pipeline

```
python main.py
```

---

### 4️⃣ Launch the dashboard

```
streamlit run streamlit_app.py
```

---

# 🎯 Business Impact

This platform enables companies to:

* Detect revenue anomalies automatically
* Forecast future demand
* Identify underperforming products and regions
* Generate AI-driven recommendations
* Enable executives to ask questions using natural language

---

# 📌 Future Improvements

Planned upgrades:

* Natural Language → SQL query generation
* Automated KPI monitoring
* Advanced anomaly detection models
* Real-time data pipelines

---

# 👨‍💻 Author

**Manas Jadhav**

Data Analyst | Power BI Developer | Aspiring Data Engineer

LinkedIn
[https://linkedin.com/in/manasjadhav0086](https://linkedin.com/in/manasjadhav08)

GitHub
[https://github.com/manasjadhav0086](https://github.com/manasjadhav0086)

---
