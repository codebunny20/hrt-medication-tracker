import json
import os

class DataManager:
    def __init__(self, data_directory=None):
        if data_directory is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            data_directory = os.path.join(base_dir, "data")
        self.data_directory = data_directory
        self.hrt_entries_file = os.path.join(data_directory, 'hrt_entries.json')
        self.hrt_resources_file = os.path.join(data_directory, 'hrt_resources.json')
        self.symptoms_file = os.path.join(data_directory, 'symptoms.json')

    def _load_list_or_wrapped(self, path, list_key):
        if not os.path.exists(path):
            return []
        with open(path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict) and list_key in data:
            return data[list_key]
        if isinstance(data, list):
            return data
        return []

    def _save_list_or_wrapped(self, path, list_key, items):
        wrapped = {list_key: items}
        with open(path, "w") as f:
            json.dump(wrapped, f, indent=4)

    def load_hrt_entries(self):
        return self._load_list_or_wrapped(self.hrt_entries_file, "entries")

    def save_hrt_entries(self, entries):
        self._save_list_or_wrapped(self.hrt_entries_file, "entries", entries)

    def load_hrt_resources(self):
        return self._load_list_or_wrapped(self.hrt_resources_file, "resources")

    def save_hrt_resources(self, resources):
        self._save_list_or_wrapped(self.hrt_resources_file, "resources", resources)

    def load_symptoms(self):
        return self._load_list_or_wrapped(self.symptoms_file, "symptoms")

    def save_symptoms(self, symptoms):
        self._save_list_or_wrapped(self.symptoms_file, "symptoms", symptoms)