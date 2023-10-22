import argparse
import json
import re
from typing_extensions import Dict
from chat_cli.conversation import Conversation
from chat_cli.constants import CONVERSATIONS_DIR, CONFIG_FILE_PATH

try:
    import readline
except ModuleNotFoundError:
    pass

def run(config: Dict):
    """Runs a chat loop with the given settings, exiting on ^D or .exit"""
    conversation = Conversation.previous(config) if config["resume"] else Conversation(config)
    while True:
        prompt = config["prompt"].replace('%t', str(conversation.tokens)).replace('%T', str(conversation.token_limit))
        try:
            user_query = input(prompt)
            if user_query == ".exit":
                raise EOFError
            if user_query == ".redo":
                conversation.redo()
            elif user_query == ".copy":
                conversation.copy_code()
            else:
                conversation.add_user_message(user_query)
        except EOFError:
            conversation.save_history()
            break
        except KeyboardInterrupt:
            print()
    # end while
# end run

def load_config(args: argparse.Namespace):
    """Loads the config file, applies any overrides from the command line
    and falls back to defaults if the others don't apply
    """
    with open(args.config, "r", encoding="utf-8") as fd:
        config = json.load(fd)

    if args.apikey is not None:
        config["apikey"] = args.apikey
    if args.prompt is not None:
        config["prompt"] = args.prompt
    if "prompt" not in config.keys():
        config["prompt"] = "%t/%T > "
    if args.model:
        config["model"] = args.model
    if "model" not in config.keys():
        config["model"] = "gpt-3.5-turbo"

    config["resume"] = args.resume

    return config
# end load_config

def search(regex: str):
    """Searches the converstations directory for all occurances of the given regex
    and prints the the line they occur on with indication of which party said it
    """
    files = CONVERSATIONS_DIR.glob("*.json")
    for file in files:
        chat_id = file.with_suffix('').name
        with open(file, "r", encoding="utf-8") as fd:
            conversation = json.load(fd)
        matched = []
        for message in conversation:
            for line in message["content"].split("\n"):
                if re.search(regex, line):
                    matched.append({"role": message["role"], "content": line})
        if len(matched) > 0:
            print(f"[{chat_id}]")
            for message in matched:
                user = message["role"]
                content = message["content"]
                print(f"[{user}] {content}")
            print()
        # end if
    # end for
# end search

def main():
    """Parses command line arguments and calls the appropriate run function"""
    parser = argparse.ArgumentParser(
            prog="Chat",
            description="CLI front-end for OpenAI ChatGPT model with saving and loading")
    parser.add_argument("--apikey", action="store",
                        help="Specify the API key to use when connection to OpenAI")
    parser.add_argument("--prompt", action="store",
                        help="Change the prompt that is displayed for input")
    parser.add_argument("--save", action="store_true",
                        help="If specified with --apikey and/or --prompt, save them to the config file")
    parser.add_argument("-f", "--config", action="store", default=CONFIG_FILE_PATH,
                        help=f"Specify an alternate file to load the configuration from (Default: {CONFIG_FILE_PATH})")
    parser.add_argument("-m", "--model", action="store",
                        help="Specify the model to use, refer to https://platform.openai.com/docs/models for list")
    parser.add_argument("--resume", action="store_true",
                        help="Resumes last conversation")
    parser.add_argument("-s", "--search", action="store",
                        help="Search your chat history for a given regex")
    args = parser.parse_args()
    config = load_config(args)

    if args.save:
        with open(args.config, "w", encoding="utf-8") as fd:
            json.dump(config, fd)
    # end if

    if args.search is not None:
        search(args.search)
    else:
        run(config)
# end main
