from rpgmv_translator.tokenizer.tokenizer_base import AbstractTokenizer
import nltk
from nltk.tokenize import word_tokenize
import nltk.data

def download_nltk_punkt_if_missing():
    try:
        # Check if 'punkt' tokenizer models are already downloaded
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        # If not present, download 'punkt'
        nltk.download('punkt')

download_nltk_punkt_if_missing()

class EnglishTokenizer(AbstractTokenizer):

    def tokenize(self, text):
        return word_tokenize(text)

    def get_token_count(self, text):
        tokens = self.tokenize(text)
        return len(tokens)