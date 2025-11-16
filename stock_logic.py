#import modules
import os
import requests
from datetime import datetime
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import uuid

ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "G6S32AHULPHG2KS5")


def fetch_time_series(symbol: str, function: str) -> dict:
    """
    Call Alpha Vantage and return the raw time series dict.
    This is based on your original code, but now uses the selected `function`
    instead of hardcoding TIME_SERIES_DAILY.
    """
    url = (
        "https://www.alphavantage.co/query"
        f"?function={function}&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    key_name = next((k for k in data.keys() if "Time Series" in k), None)
    if not key_name:
        raise ValueError("Could not find time series data in API response.")

    return data[key_name] 


def filter_series_by_date(time_series: dict, begin_date: str, end_date: str):
    """
    Apply your date-range filtering and close price extraction.
    Returns (dates_list, closing_prices_list).
    """
    dates = []
    closing_prices = []

    for date_str, daily_data in time_series.items():
        if begin_date <= date_str <= end_date:
            dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
            closing_prices.append(float(daily_data["4. close"]))

    if not dates:
        raise ValueError("No data found for the given date range.")

    #date ascending sort
    dates, closing_prices = zip(*sorted(zip(dates, closing_prices)))
    return dates, closing_prices


def generate_chart(
    symbol: str,
    dates,
    closing_prices,
    chart_type: str,
    begin_date: str,
    end_date: str,
    output_dir: str = "static/charts",
) -> str:
    """
    Your Matplotlib plotting logic, but:
    - saves to static/charts/<unique>.png
    - returns the relative path so Flask can render it in <img src=...>
    """
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10, 6))

    if chart_type.lower() == "bar":
        plt.bar(dates, closing_prices, color="skyblue", label="Closing Price")
    else:
        plt.plot(dates, closing_prices, marker="o", linestyle="-", label="Closing Price")

    plt.title(f"{symbol.upper()} Closing Prices from {begin_date} to {end_date}")
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    filename = f"{symbol}_{uuid.uuid4().hex}.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath)
    plt.close()

    #path relative
    return f"charts/{filename}"
