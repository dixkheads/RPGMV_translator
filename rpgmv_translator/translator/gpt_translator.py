import json
import re
import os
import openai
import time
from rpgmv_translator.translator.translator_base import AbstractTranslator
from rpgmv_translator.utils import contains_japanese

class GPTTranslator(AbstractTranslator):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.api_key)
        self.prompt = None

    def translate(self, texts):
        max_retries = 10
        attempts = 0
        retry_delay = 1
        self.prompt = self._build_prompt(texts)

        while attempts < max_retries:
            try:
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": self.prompt},
                    ],
                    model="gpt-3.5-turbo",
                )

                response_text = response.choices[0].message.content
                translated_dict = self._extract_dict_from_response(response_text)

                if self._is_valid_response(texts, translated_dict):
                    # Map the dictionary back to a list, using the original text if translation is missing
                    return [translated_dict.get(str(i), original_text) for i, original_text in enumerate(texts)]
                else:
                    print(f"Invalid response or format: {response_text}.")
                    attempts += 1
                    time.sleep(1)
            except openai.RateLimitError as e:
                print(f"Rate limit exceeded, retrying in {retry_delay} seconds: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            except openai.APIConnectionError as e:
                print(f"Failed to connect to OpenAI API: {e}")
                break  # Do not retry for connection errors
            except openai.APITimeoutError as e:
                print(f"OpenAI API request timed out: {e}")
                break  # Do not retry for timeout errors
            except openai.AuthenticationError as e:
                print(f"Authentication issue with the API key: {e}")
                break  # Do not retry for authentication errors
            except openai.APIError as e:
                print(f"OpenAI API returned an API Error: {e}")
                break  # Do not retry for general API errors

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
        prompt = f"Translate the following Japanese strings to Chinese. Return a single translated dictionary with the ORIGINAL JAPANESE TEXTS AS KEY. Don't translate English. Do not return anything other than a translated dictionary:\n{json_dict}"
        return prompt

    def _build_enhanced_prompt(self, texts):
        json_dict = json.dumps({str(i): text for i, text in enumerate(texts)}, ensure_ascii=False)
        prompt = f"TRANSLATE the following Japanese strings TO CHINESE. Return a single translated dictionary with the ORIGINAL JAPANESE TEXTS AS KEY. Don't translate English. Do not return anything other than a translated dictionary. Don't leave Japanese characters in the translated text:\n{json_dict}"
        return prompt

    def _is_valid_response(self, original_texts, translated_texts):
        if not isinstance(translated_texts, dict):
            print("Invalid response: The response is not a dictionary.")
            return False

        if len(translated_texts) < len(original_texts) * 0.9:
            print(f"Invalid response: Insufficient length. Expected at least {len(original_texts) * 0.9}, got {len(translated_texts)}.")
            return False

        # Check if all keys in the translated_texts are in the original_texts
        original_text_set = set(str(i) for i in range(len(original_texts)))
        if not all(key in original_text_set for key in translated_texts.keys()):
            print("Invalid response: Some keys in the translated text are not found in the original text.")
            return False

        japanese_count = sum(contains_japanese(text) for text in translated_texts.values())
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
