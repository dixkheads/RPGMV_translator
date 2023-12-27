import csv
import json
import os
from rpgmv_translator.translator.gpt_translator import GPTTranslator  # Assuming GPTTranslator is in gpt_translator.py
from utils import estimate_token_count


class GPTRequestController:
    def __init__(self, max_tokens):
        self.max_tokens = max_tokens
        self.api_key = self._load_api_key_from_config('config.json')
        self.translator = GPTTranslator(self.api_key)

    def _load_api_key_from_config(self, config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
        return config['openai_api_key']

    def process_csv(self, original_csv_path, translated_csv_path, max_tokens):
        processed_uuids = self._get_processed_uuids(translated_csv_path)
        texts_to_translate = []
        current_token_count = 0

        with open(original_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['uuid'] not in processed_uuids:
                    token_count = estimate_token_count(row['text'])

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
        sentences = sent_tokenize(text)
        segments = []
        current_segment = ""

        for sentence in sentences:
            if estimate_token_count(current_segment + sentence) <= max_tokens:
                current_segment += sentence + " "
            else:
                if current_segment:
                    segments.append(current_segment)
                current_segment = sentence + " "

                # If a single sentence is too long, split it further (naive approach)
                while estimate_token_count(current_segment) > max_tokens:
                    part = current_segment[:max_tokens]
                    remaining = current_segment[max_tokens:]
                    segments.append(part)
                    current_segment = remaining

        if current_segment:
            segments.append(current_segment)

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
