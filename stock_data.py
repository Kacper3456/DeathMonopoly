# stock_data.py
import csv
import os
import glob
from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import matplotlib.pyplot as plt

# Relative paths for CSV and chart directories
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(REPO_DIR, "Stock_prizes")
CHART_DIR = os.path.join(REPO_DIR, "Stock_charts")

# Ensure directories exist
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

def get_turn_dates(turn_counter):
    """
    Calculate start and end dates for a given turn.
    """
    start = datetime(2015, 1, 1)
    end = datetime(2015, 1, 31)  # Skrócony okres do 1 miesiąca
    start += relativedelta(months=2 * turn_counter)  # 2 miesiące zamiast 5
    end += relativedelta(months=2 * turn_counter)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

def get_data(selected_companies, turn_counter):
    """
    Download stock data from Yahoo Finance and save as CSV.
    """
    start_date, end_date = get_turn_dates(turn_counter)
    for company in selected_companies:
        ticker = yf.Ticker(company)
        data = ticker.history(start=start_date, end=end_date)
        csv_file = os.path.join(CSV_DIR, f"{company}_history.csv")
        data.to_csv(csv_file)
        print(f"Saved CSV for {company} -> {csv_file}")

def get_data_chart(company, all_prices=None):
    """
    Generate a stock chart from CSV data with color based on price change.
    """
    csv_file = os.path.join(CSV_DIR, f"{company}_history.csv")
    if not os.path.exists(csv_file):
        print(f"CSV not found for {company}, skipping chart generation.")
        return
    with open(csv_file, "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        date_idx = header.index("Date")
        close_idx = header.index("Close")
        dates, prices = [], []
        for row in reader:
            dates.append(row[date_idx])
            prices.append(float(row[close_idx]))
    
    # Określ kolor na podstawie zmiany ceny
    color = 'green' if prices[-1] >= prices[0] else 'red'
    
    # Określ skalę Y (jeśli podano all_prices)
    if all_prices is not None and len(all_prices) > 0:
        y_min = min(all_prices) * 0.95
        y_max = max(all_prices) * 1.05
    else:
        y_min = min(prices) * 0.95
        y_max = max(prices) * 1.05
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, prices, color=color, linewidth=2)
    plt.title(f"{company} Stock Price")
    plt.ylabel("Cena (USD)")
    plt.ylim(y_min, y_max)
    plt.xticks([])
    plt.grid(True, alpha=0.3)
    
    chart_file = os.path.join(CHART_DIR, f"{company}_chart.png")
    plt.savefig(chart_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved chart for {company} -> {chart_file}")

def generate_all_charts(companies):
    """
    Generate charts for all companies with unified Y-axis scale.
    """
    all_prices = []
    
    # Zbierz wszystkie ceny ze wszystkich firm
    for company in companies:
        csv_file = os.path.join(CSV_DIR, f"{company}_history.csv")
        if os.path.exists(csv_file):
            with open(csv_file, "r") as file:
                reader = csv.reader(file)
                header = next(reader)
                close_idx = header.index("Close")
                for row in reader:
                    all_prices.append(float(row[close_idx]))
    
    # Generuj wykresy z jednolitą skalą
    for company in companies:
        get_data_chart(company, all_prices)

def get_price_change(stock_name):
    """
    Returns the multiplier based on first and last closing price in CSV.
    """
    csv_file = os.path.join(CSV_DIR, f"{stock_name}_history.csv")
    if not os.path.exists(csv_file):
        print(f"CSV not found for {stock_name}")
        return 1.0
    with open(csv_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        prices = [float(row["Close"]) for row in reader if row.get("Close")]
    if not prices:
        return 1.0
    start_price = prices[0]
    end_price = prices[-1]
    if start_price == 0:
        return 1.0
    return end_price / start_price

def clear_stock_files():
    """
    Deletes all CSV and chart files.
    """
    for file in glob.glob(os.path.join(CSV_DIR, "*_history.csv")):
        try:
            os.remove(file)
        except OSError:
            pass
    for file in glob.glob(os.path.join(CHART_DIR, "*_chart.png")):
        try:
            os.remove(file)
        except OSError:
            pass