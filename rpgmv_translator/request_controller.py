import csv
import json
import os
from gpt_translator import GPTTranslator  # Assuming GPTTranslator is in gpt_translator.py


class GPTRequestController:
    def __init__(self, max_tokens):
        self.max_tokens = max_tokens
        self.api_key = self._load_api_key_from_config('config.json')
        self.translator = GPTTranslator(self.api_key)

    def _load_api_key_from_config(self, config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
        return config['openai_api_key']

    def process_csv(self, original_csv_path, translated_csv_path):
        processed_uuids = self._get_processed_uuids(translated_csv_path)

        with open(original_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['uuid'] not in processed_uuids:
                    # Split and translate text
                    translated_texts = self.translator.translate_to_chinese([row['text']])

                    # Write to translated CSV
                    self._write_to_csv(translated_csv_path, row['uuid'], translated_texts[0])

    def _get_processed_uuids(self, translated_csv_path):
        try:
            with open(translated_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                return {row['uuid'] for row in reader}
        except FileNotFoundError:
            return set()

    def _write_to_csv(self, file_path, uuid, translated_text):
        file_exists = os.path.isfile(file_path)
        with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['uuid', 'translated_text']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({'uuid': uuid, 'translated_text': translated_text})

# Example usage:
# controller = GPTRequestController(max_tokens=100)
# controller.process_csv('original.csv', 'translated.csv')
