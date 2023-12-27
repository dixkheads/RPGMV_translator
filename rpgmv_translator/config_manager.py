import json
import os

CONFIG_FILE = 'config.json'

def add_key(api_key):
    with open(CONFIG_FILE, 'w') as file:
        json.dump({'openai_api_key': api_key}, file)

def show_key():
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
        return config.get('openai_api_key', 'No key found')

def reset_config():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
