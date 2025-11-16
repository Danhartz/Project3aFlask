#import modules
from flask import Flask, render_template, request
import csv
from datetime import datetime

from stock_logic import (
    fetch_time_series,
    filter_series_by_date,
    generate_chart,
)

app = Flask(__name__)


def load_stock_symbols(csv_path="stocks.csv"):
    """
    Load stock symbols from your CSV.
    CSV columns (from your file): Symbol, Name, Sector
    """
    symbols = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbols.append({
                "symbol": row["Symbol"],
                "name": row["Name"],
                "sector": row["Sector"],
            })
    return symbols


@app.route("/", methods=["GET", "POST"])
def index():
    symbols = load_stock_symbols()
    chart_file = None
    error = None

    if request.method == "POST":
        symbol = request.form.get("symbol")
        chart_type = request.form.get("chart_type")          
        time_series_function = request.form.get("time_series")  
        begin_date = request.form.get("begin_date")
        end_date = request.form.get("end_date")

        try:
            # Basic validation like your ask_date / ask_end_date
            datetime.strptime(begin_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
            if end_date < begin_date:
                raise ValueError("End date cannot be before the beginning date.")

            ts = fetch_time_series(symbol, time_series_function)
            dates, closes = filter_series_by_date(ts, begin_date, end_date)
            chart_file = generate_chart(
                symbol, dates, closes, chart_type, begin_date, end_date
            )

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        symbols=symbols,
        chart_file=chart_file,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
