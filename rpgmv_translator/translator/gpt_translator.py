import json
import re

import openai
import time
from rpgmv_translator.translator.translator_base import AbstractTranslator

class GPTTranslator(AbstractTranslator):
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    def translate(self, texts):
        max_retries = 10
        attempts = 0

        while attempts < max_retries:
            try:
                response = openai.Completion.create(
                    model="gpt-3.5-turbo",
                    prompt=self._build_prompt(texts),
                    max_tokens=50 * len(texts),  # Adjust max_tokens as needed
                    n=1,
                    stop=None,
                    temperature=0.7
                )

                response_text = response.choices[0].text.strip()
                translated_texts = self._extract_list_from_response(response_text)

                if self._is_valid_response(texts, translated_texts):
                    return translated_texts
                else:
                    print(f"Invalid response or format: {response_text}")
                    attempts += 1
                    time.sleep(1)  # Wait a bit before retrying
            except openai.error.OpenAIError as e:
                print(f"OpenAI API error: {e}")
                attempts += 1
                time.sleep(1)  # Wait a bit before retrying

        raise Exception("Failed to get valid translation after retries.")

    def _extract_list_from_response(self, response_text):
        # Extract list-like string from response
        match = re.search(r'\[.*\]', response_text)
        if match:
            list_str = match.group(0)
            try:
                return json.loads(list_str)
            except json.JSONDecodeError:
                return None  # or handle the error as needed
        return None

    def _build_prompt(self, texts):
        # Format the list of texts as a JSON string
        json_list = json.dumps(texts, ensure_ascii=False)
        prompt = f"Translate the following Japanese strings to Chinese. Return only a single translated list. Do not translate English. Do not return anything other than a translated list:\n{json_list}"
        return prompt

    def _is_valid_response(self, original_texts, translated_texts):
        return isinstance(translated_texts, list) and len(original_texts) == len(translated_texts)

# Example usage:
# translator = GPTTranslator("your_api_key_here")
# japanese_texts = ["こんにちは", "これはテストです"]
# chinese_texts = translator.translate_to_chinese(japanese_texts)
# print(chinese_texts)
