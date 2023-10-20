import dotenv
import openai
import os
import json
import sys
from pathlib import Path
from typing_extensions import List, Self
from uuid6 import uuid7

dotenv.load_dotenv()

PROMPT = "> "
MODEL = "gpt-3.5-turbo"
CONVERSATIONS_DIR = Path(Path.home(), "Conversations")

openai.api_key = os.getenv("AUTHORIZATION")

class Conversation:
    def __init__(self: Self, messages: List = []):
        self._messages = messages
        self.id = uuid7()

        self.filename = Path(CONVERSATIONS_DIR, str(self.id) + ".json")
    # end __init__

    def get_user_message(self: Self):
        user_query = input(PROMPT)
        message = { "role": "user", "content": user_query }
        self._messages.append(message)
        response = openai.ChatCompletion.create(model=MODEL, messages=self._messages)
        response_message = response["choices"][0]["message"]
        print(response_message["content"])
        self._messages.append(response_message)
    # end get_user_message

    def save_history(self: Self):
        if not os.path.exists(CONVERSATIONS_DIR):
            os.mkdir(CONVERSATIONS_DIR)
        # end if

        with open(self.filename, "w") as fd:
            json.dump(self._messages, fd)
        # end with
    # end save_history
# end class Conversation

def main():
    last_conversation = []
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as fd:
            last_conversation = json.load(fd)
    conversation = Conversation(last_conversation)
    while True:
        try:
            conversation.get_user_message()
        except KeyboardInterrupt:
            conversation.save_history()
            break
    # end while
# end main

if __name__=="__main__":
    main()
