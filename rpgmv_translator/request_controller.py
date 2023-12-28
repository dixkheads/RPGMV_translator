import csv
import json
import os
# from rpgmv_translator.translator.gpt_translator import GPTTranslator  # Assuming GPTTranslator is in gpt_translator.py
# from utils import estimate_token_count
from rpgmv_translator.translator.gpt_translator import GPTTranslator
from rpgmv_translator.tokenizer.english_tokenizer import EnglishTokenizer
from rpgmv_translator.tokenizer.japanese_tokenizer import JapaneseTokenizer
from tqdm import tqdm


class GPTRequestController:
    def __init__(self, max_tokens, language):
        self.max_tokens = max_tokens
        self.language = language
        self.api_key = self._load_api_key_from_config('config.json')
        self.translator = GPTTranslator(self.api_key)
        self.tokenizer = self._select_tokenizer(language)

    def _load_api_key_from_config(self, file_name):
        # Get the directory of the current script
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(dir_path, file_name)

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

    def _count_tokens_and_estimate_price(self, original_csv_path):
        total_token_count = 0
        with open(original_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                token_count = self.tokenizer.get_token_count(row['text'])
                total_token_count += token_count

        # Assuming a hypothetical price per token (e.g., $0.0001 per token)
        price_per_token = 0.001/1000
        estimated_price = total_token_count * price_per_token

        return total_token_count, estimated_price

    def process_csv(self, original_csv_path, translated_csv_path):
        total_token_count, estimated_price = self._count_tokens_and_estimate_price(original_csv_path)
        print(f"Total tokens to translate: {total_token_count}")
        print(f"Estimated price for translation: ${estimated_price:.2f}")

        max_tokens = self.max_tokens
        processed_uuids = self._get_processed_uuids(translated_csv_path)
        texts_to_translate = []
        current_token_count = 0

        with open(original_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            total_rows = sum(1 for row in reader)  # Count total rows for tqdm
            csvfile.seek(0)  # Reset CSV file to start
            next(reader)  # Skip header

            for row in tqdm(reader, total=total_rows, desc="Translating..."):
                if row['uuid'] not in processed_uuids:
                    token_count = self.tokenizer.get_token_count(row['text'])

                    if token_count > max_tokens:
                        # Handle long single entries immediately
                        split_texts = self._split_text(row['text'], max_tokens)
                        for text in split_texts:
                            translated_text = self.translator.translate([text])[0]
                            self._write_to_csv(translated_csv_path, row['uuid'], translated_text)
                    else:
                        # Accumulate (uuid, text) pairs until token limit is reached
                        if current_token_count + token_count > max_tokens:
                            # Translate accumulated texts
                            uuids, texts = zip(*texts_to_translate)
                            translated_texts = self.translator.translate(list(texts))
                            for uuid, translated in zip(uuids, translated_texts):
                                self._write_to_csv(translated_csv_path, uuid, translated)
                            texts_to_translate = []
                            current_token_count = 0

                        texts_to_translate.append((row['uuid'], row['text']))
                        current_token_count += token_count

                # Translate any remaining texts
            if texts_to_translate:
                uuids, texts = zip(*texts_to_translate)
                translated_texts = self.translator.translate(list(texts))
                for uuid, translated in zip(uuids, translated_texts):
                    self._write_to_csv(translated_csv_path, uuid, translated)

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
