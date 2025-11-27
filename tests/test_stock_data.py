import pytest
import os
import csv
from game import stock_data
from game.stock_data import get_price_change, clear_stock_files, CSV_DIR

# Sprawdzanie działania funkcji get_price_change kiedy plik csv nie istnieje
def test_get_price_change_no_file():
    result = get_price_change("NON_EXISTENT")
    assert result == 1.0

# Sprawdzanie czy clear_stock_files usuwa poprawnie wszystkie pliki utworzone podczas gry
def test_clear_stock_files_creates_no_error(tmp_path):
    # Replace CSV_DIR temporarily
    import game.stock_data
    game.stock_data.CSV_DIR = tmp_path
    game.stock_data.CHART_DIR = tmp_path
    # Create dummy files
    dummy_csv = tmp_path / "AAPL_history.csv"
    dummy_csv.write_text("Date,Close\n2020-01-01,100\n2020-01-02,110\n")
    dummy_chart = tmp_path / "AAPL_chart.png"
    dummy_chart.write_text("dummy")
    clear_stock_files()
    assert not any(tmp_path.iterdir())

#Sprawdza czy get_price_change liczy poprawnie mnożnik zmiany cen akcji na podstawie danych z CSV
def test_get_price_change(tmp_path):
    csv_file = tmp_path / "TEST_stock_history.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Close"])
        writer.writerow(["2025-01-01", "100"])
        writer.writerow(["2025-01-02", "150"])

    # Tymczasowo nadpisujemy CSV_DIR
    old_dir = stock_data.CSV_DIR
    stock_data.CSV_DIR = str(tmp_path)

    multiplier = stock_data.get_price_change("TEST_stock")
    assert multiplier == 1.5

    stock_data.CSV_DIR = old_dir