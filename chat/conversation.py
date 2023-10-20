import json
from typing import Dict
import pyperclip
import platformdirs
import os
import re
import openai
from configparser import ConfigParser
from uuid6 import uuid7
from pathlib import Path
from chat.constants import *

try:
    from typing import Self, List
except ImportError:
    from typing_extensions import Self, List

CONVERSATIONS_DIR = Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR), "conversations")

class Conversation:
    """Represents a Converstaion with a particular model. Maintains conversation state"""

    def __init__(self: Self, config: Dict):
        self._messages = []
        self._model = config["model"]
        self.id = uuid7()
        self.filename = Path(CONVERSATIONS_DIR, str(self.id) + ".json")

        openai.api_key = config["apikey"]
    # end __init__

    @staticmethod
    def models():
        return [obj["id"] for obj in openai.Model.list()["data"]]
    # end models

    def add_user_message(self: Self, user_query: str):
        """Adds a new user message to the chat history and continues the conversation"""
        message = { "role": "user", "content": user_query }
        self._messages.append(message)
        self.get_model_response()
    # end get_user_message

    def save_history(self: Self):
        """Called to save the entire chat log to a JSON file"""
        CONVERSATIONS_DIR.mkdir(0o755, True, True)

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
