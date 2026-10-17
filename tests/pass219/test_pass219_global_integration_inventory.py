"""Fail-closed head-check pagination regression."""
import unittest
from unittest.mock import patch
from scripts.pass219_global_integration_inventory import all_check_runs

class CheckRunPaginationTests(unittest.TestCase):
    def test_second_page_is_required(self):
        calls=[]
        def fake(path):
            calls.append(path)
            if "page=1" in path:
                return {"total_count":101,"check_runs":[{"id":i} for i in range(100)]}
            if "page=2" in path:
                return {"total_count":101,"check_runs":[{"id":100}]}
            raise AssertionError(path)
        with patch("scripts.pass219_global_integration_inventory.api",side_effect=fake):
            found=all_check_runs("a"*40)
        self.assertEqual(len(found),101)
        self.assertEqual(len(calls),2)

    def test_truncated_checks_rejected(self):
        with patch("scripts.pass219_global_integration_inventory.api",
                   return_value={"total_count":101,"check_runs":[]}):
            with self.assertRaises(RuntimeError):
                all_check_runs("a"*40)

    def test_inconsistent_total_rejected(self):
        with patch("scripts.pass219_global_integration_inventory.api",
                   return_value={"total_count":1,"check_runs":[{},{}]}):
            with self.assertRaises(RuntimeError):
                all_check_runs("a"*40)

if __name__=="__main__":
    unittest.main()
