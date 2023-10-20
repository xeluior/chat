import dotenv
import openai
import os

dotenv.load_dotenv()

MODEL = "gpt-3.5-turbo"

def main():
    openai.api_key = os.getenv("AUTHORIZATION")
    response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": input("> ")
                }]
            )
    print(response)
# end main

if __name__=="__main__":
    main()
