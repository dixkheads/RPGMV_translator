import os
import json
import csv
import uuid
from utils import contains_japanese

class JSONHandler:
    def __init__(self, directory):
        self.directory = directory
        self.data_path = os.path.join(directory, 'data')
        self.original_csv = os.path.join(directory, 'original.csv')
        self.translated_csv = os.path.join(directory, 'translated.csv')

    def read_and_process_jsons(self):
        existing_entries = self._load_existing_entries(self.original_csv)
        new_entries = {}

        for file_name in os.listdir(self.data_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(self.data_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self._process_json(data, existing_entries, new_entries)
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)

        self._write_new_entries_to_csv(new_entries, self.original_csv)

    def _process_json(self, data, existing_entries, new_entries):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._process_json(value, existing_entries, new_entries)
                elif isinstance(value, str) and contains_japanese(value):
                    entry_uuid = existing_entries.get(value, str(uuid.uuid4()))
                    existing_entries[value] = entry_uuid
                    new_entries[value] = entry_uuid
                    data[key] = entry_uuid
        elif isinstance(data, list):
            for item in data:
                self._process_json(item, existing_entries, new_entries)

    def _load_existing_entries(self, csv_path):
        entries = {}
        try:
            with open(csv_path, mode='r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    entries[row[1]] = row[0]  # Assuming format: uuid, text
        except FileNotFoundError:
            pass
        return entries

    def _write_new_entries_to_csv(self, new_entries, csv_path):
        with open(csv_path, mode='a', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for text, entry_uuid in new_entries.items():
                writer.writerow([entry_uuid, text])

    def update_jsons_with_translations(self):
        translated_entries = self._load_translated_entries(self.translated_csv, self.original_csv)

        for file_name in os.listdir(self.data_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(self.data_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self._update_json(data, translated_entries)
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)

    def _update_json(self, data, translated_entries):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._update_json(value, translated_entries)
                elif isinstance(value, str) and value in translated_entries:
                    data[key] = translated_entries[value]
        elif isinstance(data, list):
            for item in data:
                self._update_json(item, translated_entries)

    def _load_translated_entries(self, translated_csv, original_csv):
        entries = {}
        try:
            with open(translated_csv, mode='r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    entries[row[0]] = row[1]  # Assuming format: uuid, translated_text
        except FileNotFoundError:
            with open(original_csv, mode='r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    entries[row[0]] = row[1]  # Assuming format: uuid, original_text
        return entries
