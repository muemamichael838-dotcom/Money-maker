import unittest
import os
import json
from persistence_manager import PersistenceManager
from api_proxy import get_pools

class TestMoneyMaker(unittest.TestCase):
    def setUp(self):
        os.environ["MONEY_MAKER_HOME"] = "/tmp/money_maker_test"
        os.environ["GROQ_API_KEYS"] = "key1,key2"
        self.pm = PersistenceManager()

    def test_persistence_logging(self):
        self.pm.log("INFO", "Test message", {"data": 123})
        # Check if file exists
        log_file = os.path.join(os.environ["MONEY_MAKER_HOME"], "agent.log")
        self.assertTrue(os.path.exists(log_file))
        with open(log_file, "r") as f:
            content = f.read()
            self.assertIn("Test message", content)

    def test_persistence_memory(self):
        self.pm.save_memory("test_key", {"foo": "bar"})
        val = self.pm.get_memory("test_key")
        self.assertEqual(val["foo"], "bar")

    def test_api_proxy_pools(self):
        pools = get_pools()
        self.assertIn("key1", pools["groq"])
        self.assertIn("key2", pools["groq"])

if __name__ == "__main__":
    unittest.main()
