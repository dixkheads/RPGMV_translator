import argparse
import os
import sys
from rpgmv_translator.translate import RPGMVTranslator  # Import the RPGMVTranslator class
import rpgmv_translator.config_manager as config_manager

def main():
    parser = argparse.ArgumentParser(description="RPGMV Translator Command Line Tool")
    parser.add_argument('-addkey', '--addkey', type=str, help='Add API key to config')
    parser.add_argument('-showkey', '--showkey', action='store_true', help='Show API key')
    parser.add_argument('-reset', '--reset', action='store_true', help='Reset config')
    parser.add_argument('-translate', '--translate', action='store_true', help='Start translating')

    args = parser.parse_args()

    if args.addkey:
        config_manager.add_key(args.addkey)
        print("API key added to config.")
    elif args.showkey:
        key = config_manager.show_key()
        print(f"API Key: {key}")
    elif args.reset:
        config_manager.reset_config()
        print("Config reset.")
    elif args.translate:
        print("Starting translation...")
        translator = RPGMVTranslator(args.translate)
        translator.translate()
        print("Translation completed.")

if __name__ == '__main__':
    main()
