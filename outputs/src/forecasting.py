from prophet import Prophet
import pandas as pd

def revenue_forecast(df):

    revenue = df.groupby("date")["revenue"].sum().reset_index()

    revenue = revenue.rename(columns={
        "date": "ds",
        "revenue": "y"
    })

    model = Prophet()

    model.fit(revenue)

    future = model.make_future_dataframe(periods=30)

    forecast = model.predict(future)

    forecast.to_csv("outputs/forecast_data.csv", index=False)

    return forecast