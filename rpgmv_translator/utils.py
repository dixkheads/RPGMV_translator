import os
import shutil
import re
# import nltk
# from nltk.tokenize import word_tokenize


def is_rpgmv_folder(directory):
    required_folders = ['audio', 'data', 'img']
    www_path = os.path.join(directory, 'www')

    if os.path.exists(www_path) and all(os.path.exists(os.path.join(www_path, folder)) for folder in required_folders):
        return True
    elif all(os.path.exists(os.path.join(directory, folder)) for folder in required_folders):
        return True
    return False

def copy_data_folder(directory):
    data_path = os.path.join(directory, 'data')
    backup_path = os.path.join(directory, 'data_old')
    if os.path.exists(data_path):
        shutil.copytree(data_path, backup_path, dirs_exist_ok=True)


def contains_japanese(text):
    # Regular expression that matches Japanese Hiragana and Katakana
    # Hiragana: U+3040 to U+309F, Katakana: U+30A0 to U+30FF
    japanese_regex = r'[\u3040-\u309F\u30A0-\u30FF]'

    # Check for the presence of Hiragana or Katakana
    if re.search(japanese_regex, text):
        return True

    # If needed, add additional logic here to handle Kanji more selectively
    # ...

    return False
