# abstract_translator.py

from abc import ABC, abstractmethod

class AbstractTranslator(ABC):

    @abstractmethod
    def translate(self, texts):
        """
        Translate a list of texts from the source language to the target language.
        """
        pass
