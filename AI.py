import csv
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

personalities = {
    "Wario": {
        "system_message": (
            "You are a bootleg brother of Mario named Wario. "
            "You are cheerful but quite dumb and often make financial choices based on arbitrary reasons. "
            "Because of that, whenever asked about your opinions or investments in stocks you will always "
            "pick the options based on how related to Nintendo or Italy the stock option is. "
            "You like to make puns to end all your responses, and those puns are often Italy or Nintendo related."
        ),
    },
    "Wario_Choices": {
        "system_message":
            "You are an AI for stock betting veideo game."
            "You will recive data about chosen stocks as tables of dates and stock prizes. You will also recive information about your budget"
            "You should allways spend all your budget and invest at least 1$ to each company"
            "You need to only provide an answer in the format:\n"
            "$company\n#price\n"
            "The company should be replaced with company name and price with how much you want to invest",
    }
}


# Function to read stock data from CSV
def get_stock_data(filename):
    dates = []
    prices = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            dates.append(row[0])
            prices.append(float(row[4]))  # Assuming 5th column is price
    return dates, prices


# Function to get all CSV files in the Stock_prizes folder
def get_all_stock_data():
    folder_path = os.path.join(os.path.dirname(__file__), "Stock_prizes")
    stock_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    all_data = {}
    for file in stock_files:
        path = os.path.join(folder_path, file)
        name = os.path.splitext(file)[0]  # filename without extension
        dates, prices = get_stock_data(path)
        all_data[name] = {"dates": dates, "prices": prices}
    return all_data


# Function to ask the bot a question with stock data
def ask_bot(question):
    personality = personalities["Wario_Choices"]
    stock_data = get_all_stock_data()

    user_input = question
    # Append stock data for each company
    for company, data in stock_data.items():
        stock_info = f"\nStock: {company}\nDates: {data['dates']}\nPrices: {data['prices']}"
        user_input += stock_info

    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": personality["system_message"]},
            {"role": "user", "content": user_input}
        ],
        store=True
    )

    return response.output_text