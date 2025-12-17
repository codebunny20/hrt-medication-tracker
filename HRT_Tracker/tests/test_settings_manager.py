import os
import tempfile
import unittest
from core.settings_manager import SettingsManager

class TestSettingsManager(unittest.TestCase):

    def setUp(self):
        # use a temp file so we don't affect real app_settings.json
        self.temp_dir = tempfile.TemporaryDirectory()
        self.settings_path = os.path.join(self.temp_dir.name, "app_settings.json")
        self.manager = SettingsManager(settings_file=self.settings_path)
        self.test_settings = {
            "theme": "light",
            "accent_color": "#FFFFFF"
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_settings_returns_dict(self):
        settings = self.manager.load_settings()
        self.assertIsInstance(settings, dict)

    def test_save_and_load_roundtrip(self):
        for k, v in self.test_settings.items():
            self.manager.set_setting(k, v)
        # reload from disk via a new instance
        manager2 = SettingsManager(settings_file=self.settings_path)
        settings = manager2.load_settings()
        self.assertEqual(settings["theme"], self.test_settings["theme"])
        self.assertEqual(settings["accent_color"], self.test_settings["accent_color"])

if __name__ == '__main__':
    unittest.main()