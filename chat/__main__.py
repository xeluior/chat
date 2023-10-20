import argparse
import platformdirs
from pathlib import Path
from chat.conversation import Conversation
from chat.conversation import *
from typing import Dict

try:
    import readline
except ModuleNotFoundError:
    pass

def run(config: Dict):
    conversation = Conversation.previous(config) if config["resume"] else Conversation(config)
    while True:
        try:
            user_query = input(config["prompt"])
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

def load_config(args: argparse.Namespace):
    with open(args.config, "r") as fd:
        config = json.load(fd)

    if args.apikey is not None:
        config["apikey"] = args.apikey
    if args.prompt is not None:
        config["prompt"] = args.prompt
    if "prompt" not in config.keys():
        config["prompt"] = "> "
    if args.model:
        config["model"] = args.model
    if "model" not in config.keys():
        config["model"] = "gpt-3.5-turbo"

    config["resume"] = args.resume

    return config
# end load_config

def main():
    parser = argparse.ArgumentParser(
            prog="Chat",
            description="CLI front-end for OpenAI ChatGPT model with saving and loading")
    parser.add_argument("--apikey", action="store", help="Specify the API key to use when connection to OpenAI")
    parser.add_argument("--prompt", action="store", help="Change the prompt that is displayed for input")
    parser.add_argument("--save", action="store_true", help=f"If specified with --apikey and/or --prompt, save them to the config file")
    parser.add_argument("-f", "--config", action="store", default=CONFIG_FILE_PATH, help=f"Specify an alternate file to load the configuration from (Default: {CONFIG_FILE_PATH})")
    parser.add_argument("-m", "--model", action="store", help="Specify the model to use, refer to https://platform.openai.com/docs/models for list")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    config = load_config(args)

    if args.save:
        with open(args.config, "w") as fd:
            json.dump(config, fd)
    # end if

    run(config)
# end main

if __name__=="__main__":
    main()
