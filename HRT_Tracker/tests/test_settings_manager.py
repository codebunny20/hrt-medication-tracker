import unittest
from core.settings_manager import load_settings, save_settings

class TestSettingsManager(unittest.TestCase):

    def setUp(self):
        self.test_settings = {
            "theme": "light",
            "accent_color": "#FFFFFF"
        }

    def test_load_settings(self):
        settings = load_settings()
        self.assertIsInstance(settings, dict)
        self.assertIn("theme", settings)
        self.assertIn("accent_color", settings)

    def test_save_settings(self):
        save_settings(self.test_settings)
        settings = load_settings()
        self.assertEqual(settings["theme"], self.test_settings["theme"])
        self.assertEqual(settings["accent_color"], self.test_settings["accent_color"])

if __name__ == '__main__':
    unittest.main()