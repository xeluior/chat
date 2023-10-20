import dotenv
import openai
import os
import json
import argparse
import re
import pyperclip
from pathlib import Path
from typing_extensions import List, Self
from uuid6 import uuid7

dotenv.load_dotenv()

PROMPT = "> "
CONVERSATIONS_DIR = Path(Path.home(), "Conversations")

openai.api_key = os.getenv("AUTHORIZATION")

class Conversation:
    """Represents a Converstaion with a particular model. Maintains conversation state"""

    def __init__(self: Self, messages: List = [], model: str = "gpt-3.5-turbo"):
        self._messages = messages
        self._model = model
        self.id = uuid7()

        self.filename = Path(CONVERSATIONS_DIR, str(self.id) + ".json")
    # end __init__

    def add_user_message(self: Self, user_query: str):
        """Adds a new user message to the chat history and continues the conversation"""
        message = { "role": "user", "content": user_query }
        self._messages.append(message)
        self.get_model_response()
    # end get_user_message

    def save_history(self: Self):
        """Called to save the entire chat log to a JSON file"""
        if not os.path.exists(CONVERSATIONS_DIR):
            os.mkdir(CONVERSATIONS_DIR)
        # end if

        with open(self.filename, "w") as fd:
            json.dump(self._messages, fd)
        # end with
    # end save_history

    def get_model_response(self: Self):
        """Helper to print and store the responses"""
        response = openai.ChatCompletion.create(model=self._model, messages=self._messages)
        response_message = response["choices"][0]["message"]
        print(response_message["content"])
        self._messages.append(response_message)
    # end get_model_response

    def redo(self: Self):
        """Regenerates the previous response"""
        self._messages.pop()
        self.get_model_response()
    # end redo

    def copy_code(self: Self):
        """Copies the first block of code between ``` markers in the previous response"""
        previous_response = self._messages[len(self._messages) - 1]["content"].split("\n")
        code_start = 0
        code_end = 0
        for i in range(len(previous_response)):
            if re.match("```.*", previous_response[i]):
                code_start = i + 1
                break
            # end if
        # end for

        for i in range(code_start, len(previous_response)):
            if re.match("```", previous_response[i]):
                code_end = i
                break
            # end if
        # end for

        code = os.linesep.join(previous_response[code_start:code_end])
        pyperclip.copy(code)
        print(pyperclip.paste())
    # end copy_code
# end class Conversation

def run(model: str):
    last_conversation = []
    conversation = Conversation(last_conversation, model)
    while True:
        try:
            user_query = input(PROMPT)
            if user_query == ".exit":
                raise KeyboardInterrupt
            elif user_query == ".redo":
                conversation.redo()
            elif user_query == ".copy":
                conversation.copy_code()
            else:
                conversation.add_user_message(user_query)
        except KeyboardInterrupt:
            conversation.save_history()
            break
    # end while
# end run

def main():
    models = [obj["id"] for obj in openai.Model.list()["data"]]
    parser = argparse.ArgumentParser(
            prog="Chat",
            description="CLI front-end for OpenAI ChatGPT model with saving and loading")
    parser.add_argument("-m", "--model", action="store", choices=models, default="gpt-3.5-turbo")
    args = parser.parse_args()

    run(args.model)
# end main

if __name__=="__main__":
    main()
