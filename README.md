# 🚀 AI Business Intelligence & Decision Intelligence Platform

An enterprise-grade **AI Analytics & Decision Intelligence Platform** that automates KPI monitoring, statistical anomaly detection, forward time-series forecasting, root-cause driver decomposition, and AI-powered executive decision recommendations.

Designed as a modern fusion of **Power BI / Tableau Interactive BI**, **Data Analyst Reasoning**, and **Conversational AI (LLM)**.

🔗 **Live Streamlit App:** [https://ai-analytics-platform.streamlit.app/](https://ai-analytics-platform.streamlit.app/)

---

## 📌 Business Problem & Motivation

Traditional BI dashboards display numbers (e.g. *Revenue ↓ 12%*) but fail to explain:
1. **Why did key metrics change?** (Which products or regional markets caused the variance?)
2. **Is this an isolated anomaly or an ongoing structural trend?**
3. **What is the forward demand trajectory over the next 30–90 days?**
4. **What concrete, prioritized actions should management take next?**

This platform bridges the gap between raw data warehousing, deterministic analytics, and executive decision-making.

---

## 🧠 System Architecture

```mermaid
flowchart TD
    A[Data Sources: MySQL Data Warehouse / Local Dataset] --> B[Data Loader & Integrity Pipeline]
    B --> C[Core Analytics Engine]
    
    C --> D1[KPI Engine & Period Comparison]
    C --> D2[Time-Series Velocity & Seasonality]
    C --> D3[Pareto 80/20 & Product Concentration]
    C --> D4[Regional Geographic Market Analysis]
    C --> D5[Prophet Revenue Forecasting]
    C --> D6[Statistical Anomaly Detection Z-Score/IQR]
    C --> D7[Root-Cause Driver Decomposition]
    C --> D8[Deterministic Business Health Scorecard]
    C --> D9[Data Quality & Freshness Audit]
    
    D1 & D2 & D3 & D4 & D5 & D6 & D7 & D8 & D9 --> E[AI Analyst Intent Router]
    
    E --> F{Groq LLM Active?}
    F -->|Yes| G[Groq LLM Llama-3.3-70B Reasoning]
    F -->|No / Offline| H[Deterministic Verified Python Engine]
    
    G & H --> I[Enterprise Streamlit BI Dashboard & Chatbot UI]
```

---

## 🤖 AI Business Analyst Agent Architecture

The AI Business Analyst is built on a strict **Grounding Principle**:
> **Python / Pandas analytics is the single source of truth.** The LLM never calculates or fabricates business numbers independently; verified analytics results are computed deterministically and passed to the LLM for executive explanation and contextual reasoning.

```text
User Question ("Why did revenue decline?")
        ↓
Intent Detection & Tool Routing (root_cause, anomalies, forecast, etc.)
        ↓
Deterministic Analytics Tool Execution (Python Engine)
        ↓
Verified Structured Result Metrics
        ↓
Groq LLM Reasoning (Llama-3.3-70B / Llama-3.1-8B)
        ↓
Executive Explanation + Actionable Strategic Recommendations
```

---

## 📊 Core Platform Features

| Module | Purpose & Capabilities |
| :--- | :--- |
| **📁 Self-Service Excel Engine** | Instant drag-and-drop ingestion of `.xlsx`, `.xls`, and `.csv` workbooks. Auto-sheet inspection, fuzzy regex schema mapping, and currency auto-detection. |
| **🏠 Executive Overview** | High-level KPI cards with MoM Deltas, 30-Day Moving Averages, MoM Waterfall breakdown, and 1-Click AI Executive Summary generation. |
| **🔢 Universal Number Formatter** | Configurable Indian (`Lakh` / `Crore`) and International (`K` / `M` / `B`) notation with strict metric-type discipline (currency, counts, %, ratios). |
| **📊 Performance & Trends** | Time-series aggregation (Daily / Weekly / Monthly), moving average smoothing, Period-over-Period comparisons, and Day-of-Week seasonality heatmaps. |
| **📦 Product Analytics** | Pareto 80/20 category concentration analysis, cumulative share %, Category Treemap, and ticket size distribution. |
| **🌍 Regional Analytics** | Geographic market share across 27 regional states, ranked league table, and regional expansion opportunities. |
| **📈 Forecasting Center** | Facebook Prophet time-series forecasting with 30/60/90-day configurable horizons, 80% confidence interval bands, and trend decomposition. |
| **🚨 Anomaly Center** | Statistical Z-score anomaly detector with configurable sensitivity slider, severity tiers (Critical, High, Medium, Low), and incident driver drilldowns. |
| **🔍 Root Cause & Drivers** | Mathematical variance decomposition isolating top positive and negative revenue drivers across categories and regions between periods. |
| **🏥 Business Health Scorecard** | Transparent 0–100 composite scorecard across 5 operational pillars: Growth Momentum, Revenue Stability, Concentration, Regional Breadth, and Ticket Size. |
| **🤖 AI Analyst (ChatGPT)** | Natural language analytics assistant with tool routing, structured brief cards, conversation memory, and visual chart explanations. |
| **🛡️ Data Quality Center** | Automated data integrity audit calculating Completeness, Validity, Uniqueness, Consistency, Outlier rates, and Freshness. |
| **🔎 Data Explorer & Exports** | Multi-column filterable grid with 1-click CSV/Excel downloads for datasets, anomaly logs, forecasts, and executive reports. |

---

## 📊 Built-in Dataset & Self-Service Ingestion

* **Default Built-in Data:** [`Retail data.xlsx`](file:///c:/Users/manas/OneDrive/Documents/AI-Business-KPI-recommendation-system/Retail%20data.xlsx) (`Raw Sales Data` sheet) containing 1,500 retail sales transactions (Jan 2025 – Sep 2026), generating ₹20.73M in revenue and ₹3.75M in net profit across 6 product categories and 4 regional zones.
* **Self-Service Ingestion:** Upload any custom `.xlsx`, `.xls`, or `.csv` file. The engine auto-inspects multi-sheet workbooks, cleans dirty currency strings (`₹1,25,000`, `$125,000`), performs regex column mapping (`Date`, `Revenue`, `Profit`, `Quantity`, `Product`, `Category`, `Region`), and dynamically calculates verified analytics.

---

## 🛠️ Technology Stack

- **Frontend & App Framework:** Streamlit (v1.55+), Custom Dark Glassmorphism CSS Design System
- **Interactive Visualizations:** Plotly Express & Plotly Graph Objects
- **Data Engineering & Ingestion:** Python 3.12, Pandas, NumPy, OpenPyXL
- **Machine Learning & Time-Series:** Facebook Prophet, CmdStanPy
- **AI Agent & LLM Reasoning:** Groq API SDK (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`), Python-dotenv
- **Database & Persistence:** SQLAlchemy, PyMySQL, MySQL Connector
- **Quality Assurance & Standards:** Python `compileall`, UTF-8 encoding

---

## 🚀 Quick Start & Installation

### 1️⃣ Clone or Navigate to the Repository
```bash
cd AI-Business-KPI-recommendation-system
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables (Optional for LLM)
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```
*(Note: If no API key is provided, the platform automatically runs in deterministic verified analytics mode without crashing).*

### 4️⃣ Run the Analytics Pipeline
```bash
python main.py
```

### 5️⃣ Launch the Interactive Dashboard
```bash
streamlit run app.py
```
*(Or use `streamlit run chatbot_app.py` for backward compatibility).*

---

## 📚 Interview Preparation & Resume Guide

Looking to showcase this project in interviews or on your resume? Check out the complete guide:
👉 **[INTERVIEW_PREP.md](file:///c:/Users/manas/OneDrive/Documents/AI-Business-KPI-recommendation-system/INTERVIEW_PREP.md)** — Includes 30s/60s elevator pitches, tailored resume bullet points, system architecture walkthroughs, and answers to the top 15 technical interview questions.

---

## 👨‍💻 Author

**Manas Jadhav**
- LinkedIn: [linkedin.com/in/manasjadhav0086](https://linkedin.com/in/manasjadhav08)
- GitHub: [github.com/manasjadhav0086](https://github.com/manasjadhav0086)
