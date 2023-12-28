import os
import sys
from rpgmv_translator.utils import is_rpgmv_folder, duplicate_json_files
from rpgmv_translator.json_handler import JSONHandler
from rpgmv_translator.request_controller import GPTRequestController
from rpgmv_translator.utils import read_progress_log, update_progress_log

class RPGMVTranslator:
    def __init__(self, directory):
        self.directory = directory
        self.json_handler = JSONHandler(directory)

    def translate(self):
        if not is_rpgmv_folder(self.directory):
            raise ValueError("The path is not a valid RPGMV folder.")

        progress = read_progress_log(self.directory)

        if not progress.get('duplicate_json_files'):
            duplicate_json_files(self.directory)
            update_progress_log(self.directory, 'duplicate_json_files')

        if not progress.get('read_and_process_jsons'):
            self.json_handler.read_and_process_jsons()
            update_progress_log(self.directory, 'read_and_process_jsons')

        if not progress.get('process_csv'):
            # Assuming GPTRequestController has been properly implemented
            controller = GPTRequestController(max_tokens=300, language='Japanese')
            controller.process_csv('original.csv', 'translated.csv')
            update_progress_log(self.directory, 'process_csv')

        if not progress.get('update_jsons_with_translations'):
            self.json_handler.update_jsons_with_translations()
            update_progress_log(self.directory, 'update_jsons_with_translations')

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    translator = RPGMVTranslator(directory)
    translator.translate()

if __name__ == "__main__":
    main()
