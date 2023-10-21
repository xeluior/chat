import json
import os
import re
from pathlib import Path
from typing_extensions import Self, List, Dict, Optional
import pyperclip
import openai
from uuid6 import uuid7, UUID
from chat_cli.constants import CONVERSATIONS_DIR


class Conversation:
    """Represents a Converstaion with a particular model. Maintains conversation state"""

    def __init__(
            self: Self,
            config: Dict,
            messages: Optional[List] = None,
            chat_id: UUID = uuid7()
    ):
        self._messages = messages if messages is not None else []
        self._model = config["model"]
        self.id = chat_id
        self.filename = Path(CONVERSATIONS_DIR, str(self.id) + ".json")

        openai.api_key = config["apikey"]
    # end __init__

    @staticmethod
    def models():
        """Returns the list of models"""
        return [obj["id"] for obj in openai.Model.list()["data"]]
    # end models

    @staticmethod
    def previous(config: Dict):
        """Restores the previous conversation's chat history from it's file"""
        files = CONVERSATIONS_DIR.glob("*.json")
        latest_file = next(files)
        latest_file_mtime = latest_file.stat().st_mtime
        for file in files:
            file_mtime = file.stat().st_mtime
            if file_mtime > latest_file_mtime:
                latest_file = file
                latest_file_mtime = file_mtime
        with open(latest_file, "r", encoding="utf-8") as fd:
            messages = json.load(fd)
        chat_id = latest_file.with_suffix('').name
        return Conversation(config, messages, UUID(chat_id))
    # end previous

    def add_user_message(self: Self, user_query: str):
        """Adds a new user message to the chat history and continues the conversation"""
        message = { "role": "user", "content": user_query }
        self._messages.append(message)
        self.get_model_response()
    # end get_user_message

    def save_history(self: Self):
        """Called to save the entire chat log to a JSON file"""
        CONVERSATIONS_DIR.mkdir(0o755, True, True)
        with open(self.filename, "w", encoding="utf-8") as fd:
            json.dump(self._messages, fd)
        print(f"Saved conversation to {self.filename}")
        # end with
    # end save_history

    def get_model_response(self: Self):
        """Helper to print and store the responses"""
        response = openai.ChatCompletion.create(model=self._model, messages=self._messages, stream=True)
        message = {}
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            if "role" in delta:
                message["role"] = delta["role"]
            if "content" in delta:
                print(delta["content"], end="", flush=True)
                if "content" not in message:
                    message["content"] = delta["content"]
                else:
                    message["content"] += delta["content"]
        print()
        self._messages.append(message)
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
        for i, line in enumerate(previous_response):
            if re.match("```.*", line):
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