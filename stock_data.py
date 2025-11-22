# stock_data.py
import csv
import os
import glob

import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_turn_dates(turn_counter):
    """
    Oblicza daty start i end dla danej tury.

    Args:
        turn_counter (int): aktualna tura (0-based)

    Returns:
        start_date (str), end_date (str): daty w formacie YYYY-MM-DD
    """
    # Daty początkowe dla tury 0
    start = datetime(2015, 1, 1)
    end = datetime(2015, 4, 30)

    # Każda tura przesuwa daty o 5 miesięcy
    start += relativedelta(months=5 * turn_counter)
    end += relativedelta(months=5 * turn_counter)

    # Zamiana na string w formacie YYYY-MM-DD
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    return start_str, end_str

def get_data(selected_companies, turn_counter):
    start_date, end_date = get_turn_dates(turn_counter)
    for company in selected_companies:
        selected_company = yf.Ticker(company)
        data = selected_company.history(start=start_date, end=end_date)
        data.to_csv(f"Stock_prizes/{company}_history.csv")
        pass

def get_data_chart(company):
    data_filename = f"Stock_prizes/{company}_history.csv"

    with open(data_filename, "r") as file:
        content = csv.reader(file)
        date = []
        price = []
        next(content)
        for row in content:
            date.append(row[0])
            price.append(float(row[4]))

    plt.figure()
    plt.plot(date, price)
    plt.title(f"{company} Stock Price")
    plt.savefig(f"Stock_charts/{company}_chart.png",
                dpi=300, bbox_inches="tight")
    plt.close()

def clear_stock_files():
     # Delete CSV files
    for file in glob.glob("Stock_prizes/*_history.csv"):
        try:
            os.remove(file)
        except OSError:
            pass

    # Delete chart PNG files
    for file in glob.glob("Stock_charts/*_chart.png"):
        try:
            os.remove(file)
        except OSError:
            pass