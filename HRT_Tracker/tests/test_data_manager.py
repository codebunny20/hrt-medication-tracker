import unittest
from core.data_manager import DataManager

class TestDataManager(unittest.TestCase):

    def setUp(self):
        self.data_manager = DataManager()

    def test_load_hrt_entries(self):
        entries = self.data_manager.load_hrt_entries()
        self.assertIsInstance(entries, list)

    def test_save_hrt_entries(self):
        test_entries = [{'id': 1, 'entry': 'Test entry'}]
        self.data_manager.save_hrt_entries(test_entries)
        loaded_entries = self.data_manager.load_hrt_entries()
        self.assertEqual(loaded_entries, test_entries)

    def test_load_hrt_resources(self):
        resources = self.data_manager.load_hrt_resources()
        self.assertIsInstance(resources, list)

    def test_save_hrt_resources(self):
        test_resources = [{'id': 1, 'resource': 'Test resource'}]
        self.data_manager.save_hrt_resources(test_resources)
        loaded_resources = self.data_manager.load_hrt_resources()
        self.assertEqual(loaded_resources, test_resources)

if __name__ == '__main__':
    unittest.main()