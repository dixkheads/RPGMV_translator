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

                translated_texts = response.choices[0].text.strip().split('\n')

                if self._is_valid_response(texts, translated_texts):
                    return translated_texts
                else:
                    attempts += 1
                    time.sleep(1)  # Wait a bit before retrying
            except openai.error.OpenAIError:
                attempts += 1
                time.sleep(1)  # Wait a bit before retrying

        raise Exception("Failed to get valid translation after retries.")

    def _build_prompt(self, texts):
        prompt = "Translate the following sentences to Chinese.:\n"
        for text in texts:
            prompt += f"- {text}\n"
        return prompt

    def _is_valid_response(self, original_texts, translated_texts):
        return isinstance(translated_texts, list) and len(original_texts) == len(translated_texts)

# Example usage:
# translator = GPTTranslator("your_api_key_here")
# japanese_texts = ["こんにちは", "これはテストです"]
# chinese_texts = translator.translate_to_chinese(japanese_texts)
# print(chinese_texts)
