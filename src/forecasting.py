from prophet import Prophet
import pandas as pd
from src.db_connection import get_connection


def revenue_forecast(df):

    # Aggregate daily revenue
    revenue = df.groupby("date")["revenue"].sum().reset_index()

    revenue = revenue.rename(columns={
        "date": "ds",
        "revenue": "y"
    })

    # Drop missing values
    revenue = revenue.dropna()

    print("Forecast training rows:", len(revenue))

    # Safety check
    if len(revenue) < 2:
        print("Not enough data for forecasting")
        return pd.DataFrame()

    # Create model with lower memory usage
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.8
    )

    model.fit(revenue)

    future = model.make_future_dataframe(periods=30)

    forecast = model.predict(future)

    # Save CSV
    forecast.to_csv("outputs/forecast_data.csv", index=False)

    # Save to MySQL
    engine = get_connection()

    forecast.to_sql(
        "revenue_forecast",
        engine,
        if_exists="replace",
        index=False
    )

    return forecast