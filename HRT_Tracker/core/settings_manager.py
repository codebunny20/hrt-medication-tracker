import json
import os

class SettingsManager:
    def __init__(self, settings_file=None):
        if settings_file is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            settings_file = os.path.join(base_dir, "data", "app_settings.json")
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as file:
                data = json.load(file)
        else:
            data = {}
        # ensure some defaults exist so callers can rely on them
        data.setdefault("theme", "System")
        data.setdefault("accent_color", "#3498db")
        return data

    def save_settings(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def reset_settings(self):
        self.settings = {}
        self.save_settings()