from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY")
)

personalities = {
    "Wagrio": {
        "system_message": "You are a bootleg brother of Mario named Wagio."
                          "You are chearfull but quite dumb and often make financial choices based on arbitrary reasons,"
                          "becouse of that whenever asked about your opinions or investments in stocks you will allways"
                          "pick the options based how ralated to nintendo or Italy the stock option is."
                          "You like to make puns to end all your responses and those puns are often Italy or Nintendo related.",
        "questions": [
            "If you had 5000$ and you could invest however you wanted into any stock what you would invest in and how much?",
        ]
    },
    "Base AI": {
        "system_message": "You are a basic AI module ment for picking the best stock options based on the provided data.",
        "questions": [
            "What's a fun fact about AI?",
            "Can you suggest a creative weekend activity?",
            "Write a motivational quote about learning."
        ]
    }
}

# Function to send questions to a bot
def ask_bot(name, personality):
    print(f"\n--- {name} ---")
    for q in personality["questions"]:
        response = client.responses.create(
            model="gpt-5-nano",
            input=[
                {"role": "system", "content": personality["system_message"]},
                {"role": "user", "content": q}
            ],
            store=True
        )
        print(f"Q: {q}")
        print(f"A: {response.output_text}\n")


if __name__ == "__main__":
    ask_bot("Wagrio", personalities["Wagrio"])