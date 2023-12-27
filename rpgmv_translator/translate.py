import os
import sys
from utils import is_rpgmv_folder, copy_data_folder
from json_handler import JSONHandler
from request_controller import GPTRequestController

class RPGMVTranslator:
    def __init__(self, directory):
        self.directory = directory
        self.json_handler = JSONHandler(directory)

    def translate(self):
        if not is_rpgmv_folder(self.directory):
            raise ValueError("The path is not a valid RPGMV folder.")

        copy_data_folder(self.directory)
        self.json_handler.read_and_process_jsons()

        # Assuming GPTRequestController has been properly implemented
        controller = GPTRequestController(max_tokens=100)
        controller.process_csv('original.csv', 'translated.csv')

        self.json_handler.update_jsons_with_translations()

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    translator = RPGMVTranslator(directory)
    translator.translate()

if __name__ == "__main__":
    main()
