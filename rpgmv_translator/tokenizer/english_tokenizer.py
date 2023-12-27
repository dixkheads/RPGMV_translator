from tokenizer_base import AbstractTokenizer
import nltk
from nltk.tokenize import word_tokenize

nltk.download('punkt')

class EnglishTokenizer(AbstractTokenizer):

    def tokenize(self, text):
        return word_tokenize(text)

    def get_token_count(self, text):
        tokens = self.tokenize(text)
        return len(tokens)