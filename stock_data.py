import yfinance as yf


def get_data(companies):
    for company in companies:
        selected_company = yf.Ticker(company)
        data = selected_company.history(start="2020-01-01", end="2025-01-01")
        data.to_csv(f"{company}_history.csv")
if __name__ == "__main__":
    get_data(["TSLA", "AAPL", "MSFT"])