import platformdirs
from pathlib import Path

APP_NAME = "Chat"
APP_AUTHOR = "ThreePointFive"
CONFIG_FILE_NAME = "chat.json"
CONFIG_DIR = Path(platformdirs.user_config_dir(APP_NAME, APP_AUTHOR))
CONFIG_FILE_PATH = Path(CONFIG_DIR, CONFIG_FILE_NAME)
