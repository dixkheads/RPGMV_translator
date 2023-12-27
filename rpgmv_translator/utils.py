import os
import shutil
import re
# import nltk
# from nltk.tokenize import word_tokenize


def is_rpgmv_folder(directory):
    required_folders = ['audio', 'data', 'fonts', 'movies']
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
    # Regular expression that matches Japanese character ranges
    # Hiragana: U+3040 to U+309F
    # Katakana: U+30A0 to U+30FF
    # Kanji: U+4E00 to U+9FAF
    japanese_regex = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]'
    return bool(re.search(japanese_regex, text))


def estimate_token_count(text):
    return len(text)