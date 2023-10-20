import dotenv
import openai
import os
import argparse
from chat.conversation import Conversation

try:
    import readline
except ModuleNotFoundError:
    pass

dotenv.load_dotenv()

PROMPT = "> "

openai.api_key = os.getenv("AUTHORIZATION")

def run(model: str):
    last_conversation = []
    conversation = Conversation(last_conversation, model)
    while True:
        try:
            user_query = input(PROMPT)
            if user_query == ".exit":
                raise EOFError
            elif user_query == ".redo":
                conversation.redo()
            elif user_query == ".copy":
                conversation.copy_code()
            else:
                conversation.add_user_message(user_query)
        except EOFError:
            conversation.save_history()
            break
        except KeyboardInterrupt:
            pass
    # end while
# end run

def main():
    models = [obj["id"] for obj in openai.Model.list()["data"]]
    parser = argparse.ArgumentParser(
            prog="Chat",
            description="CLI front-end for OpenAI ChatGPT model with saving and loading")
    parser.add_argument("-m", "--model", action="store", choices=models, default="gpt-3.5-turbo")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    run(args.model)
# end main

if __name__=="__main__":
    main()
