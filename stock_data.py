import csv

import yfinance as yf
import matplotlib.pyplot as plt

def get_data(companies):
    #module to import company data
    for company in companies:
        selected_company = yf.Ticker(company)
        data = selected_company.history(start="2020-01-01", end="2025-01-01")
        data.to_csv(f"{company}_history.csv")

def get_data_chart(company):
    #module to plot stock charts
    data_filename=f"{company}_history.csv"

    with open(data_filename,"r") as file:
        content=csv.reader(file)
        date=[]
        price=[]
        next(content)

        for row in content:
            date.append(row[0])
            price.append(float(row[4]))
    plt.plot(date,price)
    plt.show()

if __name__ == "__main__":
    get_data(["TSLA", "AAPL", "MSFT"])
    get_data_chart("TSLA")