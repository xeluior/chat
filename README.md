# Installation

I recommend using `pipx` for installation. Follow [pipx's documentation](https://pypa.github.io/pipx/) to install it, then run `pipx install chat-cli`.

# Building

Chat uses the `poetry` build tool.

1. [Install poetry](https://python-poetry.org/docs/#installation)
2. Clone the chat project repo
3. Run `poetry build` in the project root
4. The wheel and sdist will be built in the `dist/` directory

# Usage

`chat [-h] [--apikey APIKEY] [--prompt PROMPT] [--save] [-f CONFIG] [-m MODEL] [--resume] [-s SEARCH]`

## Options

### `-h`, `--help`

show these options and exit

### `--apikey`

Specify the API key to use when connection to OpenAI

### `--prompt`

Change the prompt that is displayed for input. The sequences %t and %T can be used to display the current token and max token count for the model, respectively. Default prompt is '%t/%T > '

### `--save`

If specified with --apikey and/or --prompt, save them to the config file

### `-f`, `--config` 

Specify an alternate file to load the configuration from (Default: $XDG_CONFIG_HOME/Chat/chat.json)

### `-m`, `--model`

Specify the model to use, refer to https://platform.openai.com/docs/models for list

### `--resume`

Resumes last conversation

### `-s`, `--search`

Search your chat history for a given regex

## Commands

When chating, the following commands perform special actions

### `.redo`

Regenerates the previous response. Removes the old response from the history

### `.copy`

Copies the first code block in the previous response to the system clipboard. Print's whats been copied

### `.exit`

Exits the application and saves the chat history. Same as encountering `EOF`. Prints the chat log location.

