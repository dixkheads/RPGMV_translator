from abc import ABC, abstractmethod


class AbstractTokenizer(ABC):

    @abstractmethod
    def tokenize(self, text):
        """
        Tokenize the given text into tokens.
        """
        pass

    @abstractmethod
    def get_token_count(self, text):
        """
        Return the count of tokens in the given text.
        """
        pass