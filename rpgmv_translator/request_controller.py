import csv
import json
import os
# from rpgmv_translator.translator.gpt_translator import GPTTranslator  # Assuming GPTTranslator is in gpt_translator.py
# from utils import estimate_token_count
from rpgmv_translator.translator.gpt_translator import GPTTranslator
from rpgmv_translator.tokenizer.english_tokenizer import EnglishTokenizer
from rpgmv_translator.tokenizer.japanese_tokenizer import JapaneseTokenizer


class GPTRequestController:
    def __init__(self, max_tokens, language):
        self.max_tokens = max_tokens
        self.language = language
        self.api_key = self._load_api_key_from_config('config.json')
        self.translator = GPTTranslator(self.api_key)
        self.tokenizer = self._select_tokenizer(language)

    def _load_api_key_from_config(self, config_path):
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
                api_key = config.get('openai_api_key')
                if not api_key:
                    raise ValueError("API key not found in config file.")
                return api_key
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at path: {config_path}")

    def _select_tokenizer(self, language):
        if language == 'English':
            return EnglishTokenizer()
        elif language == 'Japanese':
            return JapaneseTokenizer()
        else:
            raise ValueError(f"Unsupported language: {language}")

    def process_csv(self, original_csv_path, translated_csv_path, max_tokens):
        processed_uuids = self._get_processed_uuids(translated_csv_path)
        texts_to_translate = []
        current_token_count = 0

        with open(original_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['uuid'] not in processed_uuids:
                    token_count = self.tokenizer.get_token_count(row['text'])

                    if token_count > max_tokens:
                        # If a single entry is too large, split and translate immediately
                        split_texts = self._split_text(row['text'], max_tokens)
                        for text in split_texts:
                            translated_text = self.translator.translate([text])[0]
                            self._write_to_csv(translated_csv_path, row['uuid'], translated_text)
                    else:
                        # Accumulate texts until token limit
                        if current_token_count + token_count > max_tokens:
                            # Translate accumulated texts
                            translated_texts = self.translator.translate(texts_to_translate)
                            for original, translated in zip(texts_to_translate, translated_texts):
                                self._write_to_csv(translated_csv_path, row['uuid'], translated)
                            texts_to_translate = []
                            current_token_count = 0

                        texts_to_translate.append(row['text'])
                        current_token_count += token_count

            # Translate any remaining texts
            if texts_to_translate:
                translated_texts = self.translator.translate(texts_to_translate)
                for original, translated in zip(texts_to_translate, translated_texts):
                    self._write_to_csv(translated_csv_path, row['uuid'], translated)

    def _split_text(self, text, max_tokens):
        tokens = self.tokenizer.tokenize(text)
        segments = []
        current_segment = []
        current_token_count = 0

        for token in tokens:
            if current_token_count + self.tokenizer.get_token_count(token) <= max_tokens:
                current_segment.append(token)
                current_token_count += self.tokenizer.get_token_count(token)
            else:
                segments.append(' '.join(current_segment))
                current_segment = [token]
                current_token_count = self.tokenizer.get_token_count(token)

        if current_segment:
            segments.append(' '.join(current_segment))

        return segments

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
