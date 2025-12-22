import os
import tempfile
import json
import unittest
from core.data_manager import DataManager

class TestDataManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        # pre-create empty files with wrapper objects like the real app
        with open(os.path.join(self.temp_dir.name, "hrt_entries.json"), "w") as f:
            json.dump({"entries": []}, f)
        with open(os.path.join(self.temp_dir.name, "hrt_resources.json"), "w") as f:
            json.dump({"resources": []}, f)
        with open(os.path.join(self.temp_dir.name, "symptoms.json"), "w") as f:
            json.dump({"symptoms": []}, f)

        self.data_manager = DataManager(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_hrt_entries(self):
        entries = self.data_manager.load_hrt_entries()
        self.assertIsInstance(entries, list)

    def test_save_hrt_entries(self):
        test_entries = [{'entry': 'Test entry'}]
        self.data_manager.save_hrt_entries(test_entries)
        loaded_entries = self.data_manager.load_hrt_entries()
        self.assertEqual(loaded_entries, test_entries)

    def test_load_hrt_resources(self):
        resources = self.data_manager.load_hrt_resources()
        self.assertIsInstance(resources, list)

    def test_save_hrt_resources(self):
        test_resources = [{'name': 'Test resource'}]
        self.data_manager.save_hrt_resources(test_resources)
        loaded_resources = self.data_manager.load_hrt_resources()
        self.assertEqual(loaded_resources, test_resources)

    def test_save_and_load_symptoms(self):
        test_symptoms = [{'symptom': 'Headache'}]
        self.data_manager.save_symptoms(test_symptoms)
        loaded_symptoms = self.data_manager.load_symptoms()
        self.assertEqual(loaded_symptoms, test_symptoms)

if __name__ == '__main__':
    unittest.main()