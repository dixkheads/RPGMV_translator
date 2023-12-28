import argparse
import os
import sys
from rpgmv_translator.translate import RPGMVTranslator  # Import the RPGMVTranslator class
import rpgmv_translator.config_manager as config_manager
import rpgmv_translator.utils as utils

def main():
    parser = argparse.ArgumentParser(description="RPGMV Translator Command Line Tool")
    parser.add_argument('-addkey', '--addkey', type=str, help='Add API key to config')
    parser.add_argument('-showkey', '--showkey', action='store_true', help='Show API key')
    parser.add_argument('-reset', '--reset', action='store_true', help='Reset config')
    parser.add_argument('-translate', '--translate', type=str, nargs='?', const=os.getcwd(), default=None, help='Start translating. Specify the directory path (optional).')
    parser.add_argument('-restore', '--restore', type=str,
                        help='Restore data from .old backups in the specified directory')

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
    elif args.restore:
        try:
            utils.restore_from_backup(args.restore)
            print(f"Data successfully restored from backups in {args.restore}")
        except Exception as e:
            print(f"Error: {e}")
    elif args.translate is not None:
        directory = args.translate
        print("Starting translation...")
        translator = RPGMVTranslator(directory)
        translator.translate()
        print("Translation completed.")

if __name__ == '__main__':
    main()
