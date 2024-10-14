import os
import json

# Create the application directory
app_dir = os.path.expanduser("~/.protonlauncher")

CONFIG_PATH = os.path.join(app_dir, "config.json")

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def load_desktop():
    config = load_config()
    return config.get("desktop", None)

def set_desktop(desktop_dir):
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            config = load_config()
            config["desktop"] = desktop_dir
            json.dump(config, f)
    else:
        save_config({"desktop": desktop_dir})