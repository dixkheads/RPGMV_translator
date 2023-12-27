import json
import os

CONFIG_FILE = 'config.json'


def add_key(api_key):
    config = {'openai_api_key': api_key}

    # Check if the config file exists, create it if it doesn't
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as file:
            json.dump({}, file)

    # Update the config file with the new API key
    with open(CONFIG_FILE, 'r+') as file:
        existing_config = json.load(file)
        existing_config.update(config)
        file.seek(0)  # Go back to the start of the file
        json.dump(existing_config, file, indent=4)

def show_key():
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
        return config.get('openai_api_key', 'No key found')

def reset_config():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
