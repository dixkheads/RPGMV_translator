from rpgmv_translator.tokenizer.tokenizer_base import AbstractTokenizer
from sudachipy import tokenizer
from sudachipy import dictionary

class JapaneseTokenizer(AbstractTokenizer):

    def __init__(self):
        self.tokenizer_obj = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.C

    def tokenize(self, text):
        return [m.surface() for m in self.tokenizer_obj.tokenize(text, self.mode)]

    def get_token_count(self, text):
        tokens = self.tokenize(text)
        return len(tokens)