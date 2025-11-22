import csv
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

personalities = {
    "Wagrio": {
        "system_message": (
            "You are a bootleg brother of Mario named Wagrio. "
            "You are cheerful but quite dumb and often make financial choices based on arbitrary reasons. "
            "Because of that, whenever asked about your opinions or investments in stocks you will always "
            "pick the options based on how related to Nintendo or Italy the stock option is. "
            "You like to make puns to end all your responses, and those puns are often Italy or Nintendo related."
        ),
        "questions": [
            "If you had 5000$ and you could invest however you wanted into any stock what would you invest in and how much?"
        ]
    },
    "Base AI": {
        "system_message": "You are a basic AI module meant for picking the best stock options based on the provided data.",
        "questions": [
            "What's a fun fact about AI?",
            "Can you suggest a creative weekend activity?",
            "Write a motivational quote about learning."
        ]
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


# Function to send questions to a bot
def ask_bot(name, personality, stock_data=None):
    print(f"\n--- {name} ---")
    dates, prices = stock_data if stock_data else ([], [])

    for q in personality["questions"]:
        # If stock data exists, append it to the question
        if dates and prices:
            stock_info = f"\nHere is the stock data:\nDates: {dates}\nPrices: {prices}"
            user_input = q + stock_info
        else:
            user_input = q

        response = client.responses.create(
            model="gpt-5-nano",
            input=[
                {"role": "system", "content": personality["system_message"]},
                {"role": "user", "content": user_input}
            ],
            store=True
        )
        print(f"Q: {q}")
        print(f"A: {response.output_text}\n")


if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), "Stock_prizes", "test.csv")
    dates, prices = get_stock_data(csv_path)
    ask_bot("Wagrio", personalities["Wagrio"], stock_data=(dates, prices))