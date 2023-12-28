import json
import re
import os
import openai
import time
from rpgmv_translator.translator.translator_base import AbstractTranslator
from rpgmv_translator.utils import contains_japanese_strict

class GPTTranslator(AbstractTranslator):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.api_key)
        self.prompt = None

    def translate(self, texts, model="gpt-3.5-turbo", split_attempt=False):
        max_retries = 6 if not split_attempt else 2
        attempts = 0
        retry_delay = 1
        self.prompt = self._build_prompt(texts)

        while attempts < max_retries:
            try:
                response = self.client.chat.completions.create(
                    messages=[{"role": "system", "content": self.prompt}],
                    model=model,
                )

                response_text = response.choices[0].message.content
                translated_dict = self._extract_dict_from_response(response_text)

                if self._is_valid_response(texts, translated_dict):
                    return [translated_dict.get(original_text, original_text) for original_text in texts]
                else:
                    print(f"Invalid response or format: {response_text}.")
                    attempts += 1
                    if attempts > 2 and model != "gpt-4":
                        model = "gpt-4"
                        print("Switching to GPT-4 model.")
                    elif attempts > 4 and not split_attempt:
                        midpoint = len(texts) // 2
                        first_half = self.translate(texts[:midpoint], model, split_attempt=True)
                        second_half = self.translate(texts[midpoint:], model, split_attempt=True)
                        return first_half + second_half
                    time.sleep(retry_delay)
            except openai.RateLimitError as e:
                print(f"Rate limit exceeded, retrying in {retry_delay} seconds: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2
            except (openai.APIConnectionError, openai.APITimeoutError, openai.AuthenticationError, openai.APIError) as e:
                print(f"API error: {e}")
                break

        raise Exception("Failed to get valid translation after retries.")



    def _extract_dict_from_response(self, full_response):
        # Find the index of the first open curly bracket
        start_index = full_response.find('{')

        # Find the index of the last close curly bracket
        end_index = full_response.rfind('}')

        if start_index != -1 and end_index != -1:
            extracted_content = full_response[start_index:end_index + 1].strip()
            try:
                return json.loads(extracted_content)
            except json.JSONDecodeError:
                print("Failed to parse the extracted content as JSON.")
                return None
        else:
            print("Failed to find dictionary-like content in the response.")
            return None

    def _build_prompt(self, texts):
        json_dict = json.dumps({str(i): text for i, text in enumerate(texts)}, ensure_ascii=False)
        prompt = f"""Translate the following Japanese strings to Chinese. Return a single translated dictionary with the ORIGINAL JAPANESE TEXTS AS KEY and TRANSLATED CHINESE TEXTS AS VALUES. DO NOT USE INDICES AS KEYS. Don't translate English. Do not return anything other than a translated dictionary:\n{json_dict}

        The following is an example response:
        {{
            'こんにちは': '你好',
            'これはテストです': '这是一个测试',
            '奴隷たち': '奴隶们',
            'ククク、今回も教会で産ませてやろう。': '呵呵呵，这次也让她在教堂里生吧。',
            '玉袋ン中の精液、': '在睾丸里的精液，',
            'おいおい、挿れただけでか？': '喂喂，只是插入而已？'
        }}"""
        return prompt

    def _build_enhanced_prompt(self, texts):
        json_dict = json.dumps({str(i): text for i, text in enumerate(texts)}, ensure_ascii=False)
        prompt = f"""TRANSLATE the following Japanese strings TO CHINESE. Return a single translated dictionary with the ORIGINAL JAPANESE TEXTS AS KEYS and TRANSLATED CHINESE TEXTS AS VALUES. DO NOT USE INDICES AS KEYS. Don't translate English. Do not return anything other than a translated dictionary. DO NOT LEAVE ANY JAPANESE UNTRANSLATED, and the values SHOULD NOT CONTAIN JAPANESE CHARACTERS:\n{json_dict}

        The following is an example response:
        {{
            'こんにちは': '你好',
            'これはテストです': '这是一个测试',
            '奴隷たち': '奴隶们',
            'ククク、今回も教会で産ませてやろう。': '呵呵呵，这次也让她在教堂里生吧。',
            '玉袋ン中の精液、': '在睾丸里的精液，',
            'おいおい、挿れただけでか？': '喂喂，只是插入而已？'
        }}
        """
        return prompt

    def _is_valid_response(self, original_texts, translated_texts):
        if not isinstance(translated_texts, dict):
            print("Invalid response: The response is not a dictionary.")
            return False

        if len(translated_texts) < len(original_texts) * 0.9:
            print(f"Invalid response: Insufficient length. Expected at least {len(original_texts) * 0.9}, got {len(translated_texts)}.")
            return False

        if not all(key in original_texts for key in translated_texts.keys()):
            print("Invalid response: Some keys in the translated text are not found in the original text.")
            return False

        japanese_count = sum(contains_japanese_strict(text) for text in translated_texts.values())
        if japanese_count > len(translated_texts) * 0.2:
            print(f"Invalid response: More than 20% of the translated texts contain Japanese.")
            self.prompt = self._build_enhanced_prompt(original_texts)
            return False

        return True

# Example usage:
# translator = GPTTranslator("your_api_key_here")
# japanese_texts = ["こんにちは", "これはテストです"]
# chinese_texts = translator.translate_to_chinese(japanese_texts)
# print(chinese_texts)
